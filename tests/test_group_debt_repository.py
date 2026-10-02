import asyncio
import os
import unittest
import uuid

from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.schema import CreateSchema, DropSchema
from models.group_debt import DebtEntry, DebtGroup, DebtTransaction
from repositories.group_debt import GroupDebtRepository


class SharedLedger(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        url = os.getenv('GROUP_DEBT_TEST_POSTGRES_URL')
        self.schema = None
        if url:
            self.schema = 'group_debt_test_' + uuid.uuid4().hex
            self.engine = create_async_engine(url)
            async with self.engine.begin() as conn:
                await conn.execute(CreateSchema(self.schema))
            self.engine = self.engine.execution_options(schema_translate_map={None: self.schema})
        else:
            self.engine = create_async_engine('sqlite+aiosqlite:///:memory:')
            @event.listens_for(self.engine.sync_engine, 'connect')
            def foreign_keys(connection, record):
                connection.execute('PRAGMA foreign_keys=ON')
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda sync: DebtGroup.metadata.create_all(sync, tables=[
                DebtGroup.__table__, DebtTransaction.__table__, DebtEntry.__table__]))
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.repo = GroupDebtRepository(self.sessions)

    async def asyncTearDown(self):
        if self.schema:
            async with self.engine.begin() as conn:
                await conn.execute(DropSchema(self.schema, cascade=True))
        await self.engine.dispose()

    async def expense(self, transaction_id=100, payer=1, amount=600000, members=None):
        return await self.repo.record(transaction_id, 10, 20, payer, 'expense', amount,
            participants=members if members is not None else [1, 2, 3])

    async def test_billiards_example_with_next_day_and_partial_payment(self):
        await self.expense()
        self.assertEqual(await self.repo.summary(10, 20), {1: 400000, 2: -200000, 3: -200000})
        await self.expense(101, 2, 300000)
        self.assertEqual(await self.repo.summary(10, 20), {1: 300000, 2: 0, 3: -300000})
        await self.repo.record(102, 10, 20, 3, 'payment', 200000, recipient_id=1)
        self.assertEqual(await self.repo.summary(10, 20), {1: 100000, 2: 0, 3: -100000})

    async def test_repeated_confirmation_and_undo_are_idempotent(self):
        _, first = await self.expense()
        _, second = await self.expense()
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(len(await self.repo.history(10, 20)), 1)
        self.assertTrue(await self.repo.undo(100, 10, 20, 1))
        self.assertFalse(await self.repo.undo(100, 10, 20, 1))
        _, third = await self.expense()
        self.assertFalse(third)
        self.assertEqual(await self.repo.summary(10, 20), {1: 0, 2: 0, 3: 0})
        self.assertTrue((await self.repo.history(10, 20))[0].reversed)

    async def test_payment_undo_restores_debt_and_tracks_actor(self):
        await self.expense()
        await self.repo.record(101, 10, 20, 2, 'payment', 200000, recipient_id=1)
        self.assertEqual((await self.repo.summary(10, 20))[2], 0)
        await self.repo.undo(101, 10, 20, 9, manager=True)
        self.assertEqual((await self.repo.summary(10, 20))[2], -200000)
        row = (await self.repo.history(10, 20))[0]
        self.assertEqual(row.reversed_by, 9)
        self.assertIsNotNone(row.reversed_at)

    async def test_selected_subset_only_is_charged(self):
        await self.expense(amount=120001, members=[2, 1])
        self.assertEqual(await self.repo.summary(10, 20), {1: 60000, 2: -60000})

    async def test_different_participants_and_payer_preserve_old_debt(self):
        await self.expense()
        await self.expense(101, payer=4, amount=300000, members=[1, 4])
        balances = await self.repo.summary(10, 20)
        self.assertEqual(balances, {1: 250000, 2: -200000, 3: -200000, 4: 150000})
        # People absent from the next bill can still settle their old debt.
        await self.repo.record(102, 10, 20, 3, 'payment', 200000, recipient_id=1)
        self.assertEqual((await self.repo.summary(10, 20))[3], 0)
        self.assertEqual(len(await self.repo.history(10, 20)), 3)

    async def test_invalid_transactions_roll_back_completely(self):
        for actor, members in [(1, [1, 1]), (1, []), (1, list(range(1, 27)))]:
            with self.assertRaises(ValueError):
                await self.expense(payer=actor, members=members)
        with self.assertRaises(ValueError):
            await self.repo.record(100, 10, 20, 2, 'payment', 100, recipient_id=1)
        self.assertEqual(await self.repo.history(10, 20), [])
        async with self.sessions() as session:
            self.assertEqual(list(await session.scalars(select(DebtEntry))), [])
            self.assertEqual(list(await session.scalars(select(DebtGroup))), [])

    async def test_only_author_or_manager_can_undo(self):
        await self.expense()
        with self.assertRaises(ValueError):
            await self.repo.undo(100, 10, 20, 2)
        self.assertEqual((await self.repo.summary(10, 20))[1], 400000)
        self.assertTrue(await self.repo.undo(100, 10, 20, 9, manager=True))

    async def test_server_and_channel_ledgers_are_isolated(self):
        await self.expense()
        for guild_id, channel_id in [(10, 21), (11, 20)]:
            self.assertEqual(await self.repo.summary(guild_id, channel_id), {})
            self.assertEqual(await self.repo.history(guild_id, channel_id), [])
            with self.assertRaises(ValueError):
                await self.repo.undo(100, guild_id, channel_id, 1, manager=True)
            with self.assertRaises(ValueError):
                await self.repo.record(100, guild_id, channel_id, 1, 'expense', 10, participants=[1])

    async def test_existing_group_and_history_work_without_setup_or_owner_restrictions(self):
        # Legacy rows remain readable; new bills use their own participants.
        async with self.sessions() as session, session.begin():
            session.add(DebtGroup(guild_id=10, channel_id=20, owner_id=1,
                                  member_ids=[1, 2, 3], revision=7))
        await self.expense()
        await self.expense(101, payer=4, amount=120000, members=[2, 4])
        self.assertEqual(await self.repo.summary(10, 20),
                         {1: 400000, 2: -260000, 3: -200000, 4: 60000})
        await self.repo.undo(100, 10, 20, 1)
        self.assertEqual(await self.repo.summary(10, 20), {1: 0, 2: -60000, 3: 0, 4: 60000})
        self.assertEqual(len(await self.repo.history(10, 20)), 2)

    async def test_payer_can_pay_for_others_without_sharing_bill(self):
        await self.expense(payer=9, amount=120000, members=[2, 4])
        self.assertEqual(await self.repo.summary(10, 20), {9: 120000, 2: -60000, 4: -60000})

    async def test_new_repository_can_read_history_and_balances(self):
        await self.expense()
        fresh = GroupDebtRepository(self.sessions)
        self.assertEqual(await fresh.summary(10, 20), {1: 400000, 2: -200000, 3: -200000})
        rows = await fresh.history(10, 20)
        self.assertEqual(rows[0].shares, {'1': 200000, '2': 200000, '3': 200000})

    async def test_history_paginates_and_keeps_reversed_transactions(self):
        for transaction_id in range(100, 112):
            await self.expense(transaction_id)
        await self.repo.undo(111, 10, 20, 1)
        first = await self.repo.history(10, 20)
        second = await self.repo.history(10, 20, page=2)
        self.assertEqual([row.id for row in first], list(range(111, 101, -1)))
        self.assertEqual([row.id for row in second], [101, 100])
        self.assertTrue(first[0].reversed)

    @unittest.skipUnless(os.getenv('GROUP_DEBT_TEST_POSTGRES_URL'), 'PostgreSQL required for row-lock concurrency')
    async def test_concurrent_confirmations_record_only_once(self):
        outcomes = await asyncio.gather(self.expense(), self.expense())
        self.assertEqual(sorted(created for _, created in outcomes), [False, True])
        self.assertEqual(await self.repo.summary(10, 20), {1: 400000, 2: -200000, 3: -200000})

    @unittest.skipUnless(os.getenv('GROUP_DEBT_TEST_POSTGRES_URL'), 'PostgreSQL required for row-lock concurrency')
    async def test_concurrent_expenses_preserve_both_entries(self):
        await asyncio.gather(self.expense(), self.expense(101, 2, 300000))
        self.assertEqual(await self.repo.summary(10, 20), {1: 300000, 2: 0, 3: -300000})

    @unittest.skipUnless(os.getenv('GROUP_DEBT_TEST_POSTGRES_URL'), 'PostgreSQL required for row-lock concurrency')
    async def test_concurrent_payments_cannot_overpay(self):
        await self.expense()
        outcomes = await asyncio.gather(*[
            self.repo.record(txid, 10, 20, 2, 'payment', 200000, recipient_id=1)
            for txid in [101, 102]], return_exceptions=True)
        self.assertEqual(sum(isinstance(result, ValueError) for result in outcomes), 1)
        self.assertEqual(await self.repo.summary(10, 20), {1: 200000, 2: 0, 3: -200000})
        self.assertEqual(len(await self.repo.history(10, 20)), 2)

    @unittest.skipUnless(os.getenv('GROUP_DEBT_TEST_POSTGRES_URL'), 'PostgreSQL required for row-lock concurrency')
    async def test_concurrent_undo_applies_once(self):
        await self.expense()
        outcomes = await asyncio.gather(self.repo.undo(100, 10, 20, 1), self.repo.undo(100, 10, 20, 1))
        self.assertEqual(sorted(outcomes), [False, True])
        self.assertEqual(await self.repo.summary(10, 20), {1: 0, 2: 0, 3: 0})
