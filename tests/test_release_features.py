import copy
import random
import unittest
from unittest.mock import patch
from services.cultivation import engine as E, rules as R
from bot.cogs.cultivation import inventory_lines, paginate, BagView, Personal


class Features(unittest.TestCase):
    def setUp(self):
        self.now = 1800000000
        self.rng = random.Random(2)
        self.s = E.initial()
        self.p = E.player(self.s, 1, 'One', self.now, self.rng)
        E.player(self.s, 2, 'Two', self.now, self.rng)

    def act(self, op, **args):
        return E.execute(self.s, 1, op, args, self.now, self.rng, op)

    def test_research_optional_recipe_persists(self):
        with self.assertRaises(E.GameError):
            self.act('learn', item='focus')
        self.s['sect']['buildings']['library'] = 1
        self.act('learn', item='focus')
        self.s['sect']['buildings']['library'] = 0
        E.give(self.p, 'flower', 1)
        E.give(self.p, 'water', 2)
        self.act('craft', item='focus')
        E.settle(self.s, self.now+1000)
        self.assertEqual(E.bag(self.p, 'focus')+E.bag(self.p, 'focus', quality='fine'), 1)
        self.act('focus')
        self.assertIn(self.p['focus_buff'], (.1, .15))

    def test_old_realm_superior_gift(self):
        self.p['realm'] = 1
        E.give(self.p, 'heal', 1, 0, 'fine')
        self.act('gift', item='heal', count=1, target=2, realm=0, quality='fine')
        self.assertEqual(E.bag(self.s['players']['2'], 'heal', 0, 'fine'), 1)
        self.assertEqual(E.bag(self.p, 'heal', 0, 'fine'), 0)

    def test_notifications_opt_in_and_disabled_default(self):
        self.act('explore')
        E.settle(self.s, self.now+1500)
        self.assertFalse(self.s['outbox'])
        self.now += 2000
        self.act('notifications')
        self.act('explore')
        E.settle(self.s, self.now+1500)
        self.assertEqual(len(self.s['outbox']), 1)
        self.assertEqual(next(iter(self.s['outbox'].values()))['kind'], 'private')

    def test_achievement_only_major_breakthrough(self):
        self.p.update(tier=8, xp=675, coins=1000, insight=10)
        E.give(self.p, 'major', 1)
        E.give(self.p, 'relic', 1)
        self.act('breakthrough')
        self.assertEqual(next(iter(self.s['outbox'].values()))['kind'], 'achievement')

    def test_dungeon_choice_representative_only_and_timeout_safe(self):
        for user in ('1', '2'):
            self.s['players'][user]['tier'] = 8
        stage = {'won': True, 'seconds': 30, 'log': [], 'participants': {
            u: {'used': 0, 'health': .8, 'mana': 50, 'damage': 200} for u in ('1', '2')}}
        with patch('services.cultivation.engine.battle', return_value=copy.deepcopy(stage)):
            E.start_battle(self.s, ['1', '2'], 'dungeon', self.now, self.rng, 'team')
        self.now += 31
        with self.assertRaises(E.GameError):
            E.execute(self.s, 2, 'dungeon_event', {'choice': 'open'}, self.now, self.rng, 'wrong')
        self.act('dungeon_event', choice='open')
        with self.assertRaises(E.GameError):
            self.act('dungeon_event', choice='inspect')
        E.settle(self.s, self.now+1000)
        self.assertFalse(self.s['jobs'])
        self.assertGreaterEqual(self.p['coins'], 150+12)

    def test_stale_week_votes_reset_even_without_contributions(self):
        self.act('vote', building='garden')
        self.assertTrue(self.s['sect']['votes'])
        E.settle(self.s, self.now+8*86400)
        self.assertFalse(self.s['sect']['votes'])

    def test_dynamic_boss_target_is_locked_for_week(self):
        target = E.boss_target(self.s)
        E.player(self.s, 3, 'Three', self.now, self.rng)
        self.assertEqual(E.boss_target(self.s), target)

    def test_old_week_boss_damage_not_applied_to_new_boss(self):
        E.upgrade_state(self.s, self.now)
        old_week = R.week_key(self.now)
        later = self.now+8*86400
        self.s['jobs']['old'] = {'kind':'combat','realm':0,'users':['1'],
            'due':later, 'reward_week':old_week, 'results':{'1':{'message':'done','boss_damage':1000}}}
        E.settle(self.s, later)
        self.assertEqual(self.s['sect']['boss_damage'], 0)

    def test_inventory_filter_and_discord_length(self):
        for r in range(5):
            for item in R.NAMES:
                E.give(self.p, item, 1, r, 'fine')
        lines = inventory_lines(self.p, 'heal', 0, 'fine')
        self.assertEqual(len(lines), 1)
        pages = paginate(inventory_lines(self.p))
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(len(p) <= 1750 for p in pages))
        self.assertEqual(''.join(paginate(['x'*6000])), 'x'*6000)


class Views(unittest.IsolatedAsyncioTestCase):
    async def test_component_limits_and_owner_guard(self):
        s = E.initial()
        p = E.player(s, 1, 'One', 1800000000, random.Random(1))
        for view in (Personal(None, 1), BagView(None, 1, p)):
            data = view.to_components()
            self.assertLessEqual(len(data), 5)
            for row in data:
                for component in row['components']:
                    self.assertLessEqual(len(component.get('options', [])), 25)

if __name__ == '__main__':
    unittest.main()
