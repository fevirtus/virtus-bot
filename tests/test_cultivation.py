import asyncio
import copy
import os
import random
import time
import unittest
from unittest.mock import patch

from services.cultivation import engine as E, rules as R
from services.cultivation.combat import battle


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.s = E.initial()
        self.now = 1_800_000_000
        self.p = E.player(self.s, 1, 'Tester', self.now, random.Random(1))

    def act(self, op, **args):
        return E.execute(self.s, 1, op, args, self.now, random.Random(1), str(len(self.s['jobs'])+1))

    def test_pause_keeps_already_promised_rewards(self):
        self.act('explore')
        self.act('toggle')
        E.settle(self.s, self.now+1500)
        self.assertEqual(self.p['xp'], 20)
        self.assertEqual(E.xp(self.p, 10, self.now+1500, social=True), 0)

    def test_superior_healing_inventory_is_usable(self):
        E.give(self.p, 'heal', 2, quality='fine')
        self.p['potions'] = 2
        self.act('hunt')
        E.settle(self.s, self.now+1000)
        self.assertGreaterEqual(E.bag(self.p, 'heal', quality='fine'), 0)
        self.assertLessEqual(E.bag(self.p, 'heal', quality='fine'), 2)

    def test_weekly_rewards_and_garden_once_per_period(self):
        self.s['sect']['buildings']['garden'] = 1
        self.act('garden')
        with self.assertRaises(E.GameError):
            self.act('garden')
        E.points(self.s, '1', 100, self.now)
        self.act('weekly')
        with self.assertRaises(E.GameError):
            self.act('weekly')
        self.assertEqual(E.bag(self.p, 'flower'), 2)

    def test_late_job_cannot_reset_new_week(self):
        E.points(self.s, '1', 20, self.now+7*86400)
        new_week = self.s['sect']['week']
        E.points(self.s, '1', 3, self.now)
        self.assertEqual(self.s['sect']['week'], new_week)
        self.assertEqual(self.s['sect']['progress'], 20)
        self.assertEqual(self.s['sect']['fund'], 23)

    def test_social_cap_and_injury(self):
        self.p['realm'] = 3
        self.p['tier'] = 8
        self.assertEqual(E.xp(self.p, 800, self.now, True), 650)
        self.assertEqual(E.xp(self.p, 2000, self.now, True), 250)
        self.assertEqual(E.xp(self.p, 10, self.now, True), 0)
        self.assertEqual(E.bag(self.p, 'herb'), 2)
        self.assertEqual(E.bag(self.p, 'water'), 1)
        self.p['injury_until'] = self.now+3600
        self.assertEqual(E.xp(self.p, 100, self.now), 50)

    def test_daily_reset_at_four_ict(self):
        from datetime import datetime, timezone
        before = datetime(2026, 9, 23, 20, 59, 59, tzinfo=timezone.utc).timestamp()
        self.assertNotEqual(R.day_key(before), R.day_key(before+1))

    def test_roll_locks_after_first_breakthrough(self):
        self.act('roll')
        self.assertIsNotNone(self.p['candidate'])
        self.p['xp'] = R.cap(self.p)
        E.give(self.p, 'minor', 1)
        self.act('breakthrough')
        self.assertTrue(self.p['roll_locked'])
        self.assertIsNone(self.p['candidate'])
        with self.assertRaises(E.GameError):
            self.act('roll')

    def test_failure_and_pity(self):
        self.p.update(tier=8, xp=675, coins=10000)
        E.give(self.p, 'major', 5)
        E.give(self.p, 'relic', 5)
        rng = random.Random(1)
        with patch.object(rng, 'random', return_value=.999):
            for attempt in range(4):
                self.now += 90000
                self.p['xp'] = R.cap(self.p)
                E.execute(self.s, 1, 'breakthrough', {}, self.now, rng, str(attempt))
                self.assertEqual(self.p['insight'], attempt+1)
                self.assertAlmostEqual(self.p['xp'], 607.5)
            self.now += 90000
            self.p['xp'] = R.cap(self.p)
            E.execute(self.s, 1, 'breakthrough', {}, self.now, rng, 'last')
        self.assertEqual(self.p['realm'], 1)

    def test_craft_settles_once_after_restart(self):
        E.give(self.p, 'herb', 10)
        E.give(self.p, 'water', 10)
        self.act('craft', item='minor', count=2)
        import json
        state = json.loads(json.dumps(self.s))
        E.settle(state, self.now+1000)
        E.settle(state, self.now+2000)
        p = state['players']['1']
        self.assertEqual(E.bag(p, 'minor'), 2)
        self.assertEqual(p['coins'], 134)
        self.assertEqual(len(p['inbox']), 1)

    def test_craft_failure_refund_and_pity(self):
        self.p['coins'] = 10000
        for item in ('herb', 'water', 'core'):
            E.give(self.p, item, 100)
        rng = random.Random(1)
        with patch.object(rng, 'random', return_value=.99):
            E.execute(self.s, 1, 'craft', {'item': 'major', 'count': 3}, self.now, rng, 'craft')
        E.settle(self.s, self.now+10000)
        self.assertEqual(E.bag(self.p, 'major'), 1)
        self.assertEqual(E.bag(self.p, 'core'), 96)
        self.assertEqual(self.p['craft_pity']['0:major'], 0)

    def test_same_realm_party_ready_required(self):
        E.player(self.s, 2, 'Friend', self.now, random.Random(2))
        room = self.act('room_create')
        E.execute(self.s, 2, 'room_join', {'room': room}, self.now, random.Random(2), 'join')
        with self.assertRaises(E.GameError):
            self.act('room_start', room=room)
        self.act('room_ready', room=room)
        E.execute(self.s, 2, 'room_ready', {'room': room}, self.now, random.Random(2), 'ready')
        self.act('room_start', room=room)
        self.assertFalse(self.s['rooms'])
        self.assertEqual(len(self.s['jobs']), 1)

    def test_locked_item_cannot_be_gifted(self):
        E.player(self.s, 2, 'Friend', self.now, random.Random(2))
        E.give(self.p, 'relic', 1)
        with self.assertRaises(E.GameError):
            self.act('gift', target=2, item='relic', count=1)
        self.assertEqual(E.bag(self.p, 'relic'), 1)

    def test_combat_reproducible_and_bounded(self):
        self.p['_potions'] = 2
        a = battle([('1', self.p)], 0, 'boss', 42)
        self.assertEqual(a, battle([('1', self.p)], 0, 'boss', 42))
        self.assertLessEqual(a['participants']['1']['used'], 2)
        self.assertGreaterEqual(a['seconds'], 30)

    def test_partial_dungeon_keeps_first_stage_reward(self):
        stage = {'won': True, 'seconds': 30, 'log': [], 'participants': {'1': {'used': 0, 'health': .5, 'mana': 50}}}
        boss = copy.deepcopy(stage)
        boss['won'] = False
        with patch('services.cultivation.engine.battle', side_effect=[stage, boss]):
            self.act('dungeon')
        E.settle(self.s, self.now+1000)
        self.assertEqual(E.bag(self.p, 'blood'), 1)
        self.assertEqual(E.bag(self.p, 'core'), 0)
        self.assertEqual(self.p['daily']['dungeon'], 1)

    def test_event_is_hidden_until_explicit_choice_and_safe_timeout(self):
        self.p['event'] = {'seed': 1, 'fortune': 50, 'calamity': 50, 'realm': 0, 'expires': self.now+30}
        E.settle(self.s, self.now+31)
        self.assertIsNone(self.p['event'])
        self.assertEqual(self.p['coins'], 150)


@unittest.skipUnless(os.getenv('CULTIVATION_TEST_DATABASE_URL'), 'Requires isolated PostgreSQL')
class StoreTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from infra.db.base import Base
        from services.cultivation.store import GameStore
        self.engine = create_async_engine(os.environ['CULTIVATION_TEST_DATABASE_URL'])
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.store = GameStore(async_sessionmaker(self.engine, expire_on_commit=False))
        self.gid = random.randint(10000000, 999999999)

    async def asyncTearDown(self):
        from sqlalchemy import delete
        from models.cultivation import CultivationGuild, CultivationReceipt
        async with self.engine.begin() as conn:
            await conn.execute(delete(CultivationReceipt).where(CultivationReceipt.guild_id.in_([self.gid, self.gid+1])))
            await conn.execute(delete(CultivationGuild).where(CultivationGuild.guild_id.in_([self.gid, self.gid+1])))
        await self.engine.dispose()

    async def test_duplicate_and_concurrent_spending(self):
        await self.store.snapshot(self.gid, 1)
        async def buy(action):
            return await self.store.act(self.gid, 1, 'A', action, 'buy', {'item': 'herb', 'count': 5})
        await asyncio.gather(buy('same'), buy('same'))
        s, _ = await self.store.snapshot(self.gid)
        self.assertEqual(s['players']['1']['coins'], 130)
        results = await asyncio.gather(buy('a'), buy('b'), return_exceptions=True)
        self.assertEqual(sum(isinstance(r, E.GameError) for r in results), 1)
        s, _ = await self.store.snapshot(self.gid)
        self.assertEqual(s['players']['1']['coins'], 110)
        self.assertEqual(E.bag(s['players']['1'], 'herb'), 10)

    async def test_failed_action_rolls_back_everything(self):
        await self.store.snapshot(self.gid, 1)
        async with self.store.locked(self.gid) as (_, row):
            E.give(row.state['players']['1'], 'herb', 2)
        with self.assertRaises(E.GameError):
            await self.store.act(self.gid, 1, 'A', 'bad', 'craft', {'item': 'minor'})
        s, _ = await self.store.snapshot(self.gid)
        self.assertEqual(E.bag(s['players']['1'], 'herb'), 2)
        self.assertEqual(s['players']['1']['coins'], 150)
        self.assertFalse(s['jobs'])

    async def test_guild_isolation(self):
        await self.store.act(self.gid, 1, 'A', 'buy', 'buy', {'item': 'herb'})
        s, _ = await self.store.snapshot(self.gid+1, 1)
        self.assertEqual(s['players']['1']['coins'], 150)
        self.assertFalse(s['players']['1']['inventory'])

    async def test_chat_and_voice_overlap(self):
        await self.store.reward_chat(self.gid, 1, 'A', 100, 'hello')
        await self.store.reward_chat(self.gid, 1, 'A', 101, 'hello')
        now = time.time()
        await self.store.reward_voice(self.gid, 1, 'A', 'v1', 30, end=now)
        await self.store.reward_voice(self.gid, 1, 'A', 'v2', 30, end=now)
        s, _ = await self.store.snapshot(self.gid)
        self.assertAlmostEqual(s['players']['1']['xp'], 12)

    async def test_stale_quote_refused_without_spend(self):
        s, _ = await self.store.snapshot(self.gid, 1)
        quoted = E.quote(s, 1, 'roll', {})
        async with self.store.locked(self.gid) as (_, row):
            row.state['players']['1']['roll_locked'] = True
        with self.assertRaises(E.GameError):
            await self.store.act(self.gid, 1, 'A', 'old', 'roll', {'_quote': quoted})
        s, _ = await self.store.snapshot(self.gid)
        self.assertEqual(s['players']['1']['coins'], 150)


if __name__ == '__main__':
    unittest.main()
