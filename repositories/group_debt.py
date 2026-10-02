from datetime import datetime, timezone
from sqlalchemy import func, select
from models.group_debt import DebtEntry, DebtGroup, DebtTransaction
from services.group_debt import expense_deltas, payment_deltas, split_shares


class GroupDebtRepository:
    def __init__(self, session_maker=None):
        if session_maker is None:
            from infra.db import postgres
            session_maker = postgres.get_sessionmaker()
        self.Session = session_maker

    async def _lock_group(self, session, guild_id, channel_id):
        group = await session.scalar(select(DebtGroup).where(
            DebtGroup.guild_id == guild_id, DebtGroup.channel_id == channel_id
        ).with_for_update())
        if group is None:
            raise ValueError("Kênh này chưa có giao dịch. Dùng /chia để ghi khoản đầu tiên.")
        return group

    async def _ensure_ledger(self, session, guild_id, channel_id, actor_id):
        # Retain the existing table/FK as a channel lock, with no roster setup.
        # Concurrent first bills safely create one row before acquiring its lock.
        if session.bind.dialect.name == 'sqlite':
            from sqlalchemy.dialects.sqlite import insert
        else:
            from sqlalchemy.dialects.postgresql import insert
        await session.execute(insert(DebtGroup).values(
            guild_id=guild_id, channel_id=channel_id, owner_id=actor_id,
            member_ids=[], revision=1,
        ).on_conflict_do_nothing(index_elements=['guild_id', 'channel_id']))

    async def _balances(self, session, guild_id, channel_id):
        rows = await session.execute(select(DebtEntry.user_id, func.sum(DebtEntry.delta)).join(
            DebtTransaction, DebtEntry.transaction_id == DebtTransaction.id
        ).where(DebtTransaction.guild_id == guild_id, DebtTransaction.channel_id == channel_id,
                DebtTransaction.reversed.is_(False)).group_by(DebtEntry.user_id))
        return {user_id: int(value) for user_id, value in rows}

    async def summary(self, guild_id, channel_id):
        async with self.Session() as session:
            group = await session.get(DebtGroup, (guild_id, channel_id))
            balances = await self._balances(session, guild_id, channel_id)
            for user_id in group.member_ids if group else []:
                balances.setdefault(user_id, 0)
            return balances

    async def record(self, transaction_id, guild_id, channel_id, actor_id, kind, amount,
                     participants=None, recipient_id=None, note=""):
        if kind not in ('expense', 'payment') or len(note) > 100:
            raise ValueError("Giao dịch không hợp lệ; ghi chú tối đa 100 ký tự.")
        async with self.Session() as session, session.begin():
            if kind == 'expense':
                await self._ensure_ledger(session, guild_id, channel_id, actor_id)
            group = await self._lock_group(session, guild_id, channel_id)
            existing = await session.get(DebtTransaction, transaction_id)
            if existing:
                if (existing.guild_id, existing.channel_id, existing.actor_id) != (guild_id, channel_id, actor_id):
                    raise ValueError("Giao dịch không thuộc nhóm này.")
                return existing, False
            balances = await self._balances(session, guild_id, channel_id)
            if kind == 'expense':
                shares = split_shares(amount, participants or [])
                deltas = expense_deltas(amount, actor_id, shares)
                # Keep zero balances visible after undo, including legacy members.
                group.member_ids = sorted(set(group.member_ids) | set(deltas))
            else:
                shares = {}
                deltas = payment_deltas(amount, actor_id, recipient_id, balances)
            transaction = DebtTransaction(
                id=transaction_id, guild_id=guild_id, channel_id=channel_id, actor_id=actor_id,
                kind=kind, amount=amount, recipient_id=recipient_id, note=note,
                shares={str(uid): value for uid, value in shares.items()},
            )
            session.add(transaction)
            await session.flush()
            session.add_all([DebtEntry(transaction_id=transaction_id, user_id=uid, delta=delta)
                             for uid, delta in deltas.items()])
            return transaction, True

    async def undo(self, transaction_id, guild_id, channel_id, actor_id, manager=False):
        async with self.Session() as session, session.begin():
            await self._lock_group(session, guild_id, channel_id)
            transaction = await session.get(DebtTransaction, transaction_id)
            if not transaction or (transaction.guild_id, transaction.channel_id) != (guild_id, channel_id):
                raise ValueError("Không tìm thấy giao dịch trong kênh này.")
            if transaction.actor_id != actor_id and not manager:
                raise ValueError("Bạn chỉ được hoàn tác giao dịch của mình.")
            if transaction.reversed:
                return False
            transaction.reversed = True
            transaction.reversed_by = actor_id
            transaction.reversed_at = datetime.now(timezone.utc)
            return True

    async def history(self, guild_id, channel_id, page=1):
        async with self.Session() as session:
            rows = await session.scalars(select(DebtTransaction).where(
                DebtTransaction.guild_id == guild_id, DebtTransaction.channel_id == channel_id
            ).order_by(DebtTransaction.id.desc()).offset((page - 1) * 10).limit(10))
            return list(rows)
