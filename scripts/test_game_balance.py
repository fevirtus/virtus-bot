"""Regression checks for the offline balance model, not production game tests."""
import copy
import json
import random
import unittest
from pathlib import Path

from simulate_game_balance import Player, fight, simulate

CONFIG = json.loads((Path(__file__).resolve().parents[1]/'docs/game/balance/candidate-004.json').read_text())


class BalanceTests(unittest.TestCase):
    def config(self):
        c = copy.deepcopy(CONFIG)
        c['realms'] = c['realms'][:1]
        c['horizon_days'] = 40
        return c

    def test_reproducible_progression(self):
        c = self.config()
        self.assertEqual(simulate(c, 3, ['moderate']), simulate(c, 3, ['moderate']))

    def test_money_conservation_and_no_negative_inventory(self):
        c = self.config()
        for seed in range(10):
            r = Player(c, c['profiles']['moderate'], seed).run()
            income = sum(v for k, v in r['metrics'].items() if k.startswith('income_'))
            spent = sum(v for k, v in r['metrics'].items() if k.startswith('spent_'))
            self.assertEqual(r['final_coins'], c['initial_coins']+income-spent)
            self.assertTrue(all(v >= 0 for bag in r['stock'] for v in bag.values()))

    def test_potion_cap_and_rng_replay(self):
        for party in (1, 3):
            for budget in (0, 1, 2):
                args = (CONFIG, 0, 0, 'boss', party, 'balanced', False, budget, 1)
                a = fight(random.Random(7), *args)
                self.assertEqual(a, fight(random.Random(7), *args))
                self.assertLessEqual(a[2], budget)

    def test_shop_restrictions_and_transaction(self):
        c = self.config()
        p = Player(c, c['profiles']['moderate'], 1)
        coins = p.coins
        self.assertFalse(p.procure({'core': 1, 'coins': 1}, 0))
        self.assertEqual(p.coins, coins)
        self.assertFalse(p.procure({'herb': c['shop_daily_units']+1, 'coins': 1}, 0))
        self.assertEqual(p.coins, coins)
        self.assertTrue(p.procure({'herb': 2, 'coins': 1}, 0))
        self.assertEqual(p.coins, coins-2*c['shop_prices']['herb'])

    def test_no_fixed_one_tier_per_day(self):
        c = self.config()
        c['realms'][0]['xp'] = [10]*9
        p = Player(c, c['profiles']['at_cap'], 1)
        p.stock[0].update(minor=20, major=1, relic=1)
        p.queue = [(t, t, 'social', (0, 50)) for t in range(1, 8)]
        r = p.run()
        self.assertGreaterEqual(r['tier'], 6)

    def test_injury_prevents_breakthrough(self):
        c = self.config()
        p = Player(c, c['profiles']['moderate'], 1)
        p.tier = 8
        p.xp = c['realms'][0]['xp'][8]
        p.stock[0].update(major=1, relic=1)
        p.injured_until = 100
        p.progress(50, allow_start=False)
        self.assertEqual(p.realm, 0)
        self.assertEqual(p.stock[0]['major'], 1)

    def test_crafting_pity_without_free_items(self):
        c = self.config()
        c['realms'][0]['craft_success'] = 0
        p = Player(c, c['profiles']['moderate'], 1)
        p.queue = []
        p.coins = c['initial_coins'] = 10000
        p.stock[0].update(herb=100, water=100, core=100)
        # Explicitly start each attempt and suppress unrelated progression.
        p.busy = True
        for i in range(3):
            self.assertTrue(p.start_craft('major', i*20))
            # run() resets busy; tier 0 progress cannot consume a major pill.
            p.run()
        self.assertEqual(p.stock[0]['major'], 1)
        self.assertEqual(p.metrics['craft_failures'], 2)
        self.assertEqual(p.metrics['spent_craft'], 3*c['recipes']['major']['coins'])

    def test_breakthrough_guarantee_and_xp_penalty(self):
        c = self.config()
        p = Player(c, c['profiles']['moderate'], 1)
        class Unlucky:
            def random(self):
                return .999999
        p.progress_rng = Unlucky()
        p.coins = 10000
        p.tier = 8
        p.stock[0].update(major=5, relic=5)
        maximum = c['realms'][0]['xp'][8]
        for attempt in range(4):
            p.xp = maximum
            p.progress(attempt*1440, allow_start=False)
            self.assertAlmostEqual(p.xp, .9*maximum)
            self.assertEqual(p.metrics['break_failures'], attempt+1)
        p.xp = maximum
        p.progress(4*1440, allow_start=False)
        self.assertTrue(p.finished)
        self.assertEqual(len(p.milestones), 1)

    def test_offline_craft_completion_and_social_cap(self):
        c = self.config()
        p = Player(c, c['profiles']['moderate'], 1)
        p.queue = []
        p.stock[0].update(herb=2, water=1)
        self.assertTrue(p.start_craft('minor', 0))
        p.run()
        self.assertEqual(p.stock[0]['minor'], 1)
        p.queue = []
        for t in range(24):
            p.add(t, 'social', (0, 100))
        p.run()
        self.assertLessEqual(p.day_social[0], 900)


if __name__ == '__main__':
    unittest.main()
