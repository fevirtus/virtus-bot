import random
import unittest
from services.group_debt import expense_deltas, money, parse_amount, payment_deltas, settlements, split_shares


class MoneyRules(unittest.TestCase):
    def test_accepts_dong_and_k_without_silent_rounding(self):
        for text, expected in [('600000', 600000), ('600k', 600000), (' 150.5K ', 150500), ('150,5k', 150500), ('0.001k', 1)]:
            with self.subTest(text=text):
                self.assertEqual(parse_amount(text), expected)
        for text in ['', '0', '-1', '600.000', 'NaN', '1e6', '100₫', '0.0001k', '1000000000001', '1kk']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_amount(text)
        self.assertEqual(money(200000), '200.000 ₫')

    def test_rounding_is_exact_and_independent_of_selection_order(self):
        self.assertEqual(split_shares(100, [30, 10, 20]), {10: 34, 20: 33, 30: 33})
        self.assertEqual(split_shares(1, [3, 2, 1]), {1: 1, 2: 0, 3: 0})
        for members in ([], [1, 1], list(range(26))):
            with self.assertRaises(ValueError):
                split_shares(100, members)

    def test_payer_can_be_excluded_from_shared_cost(self):
        self.assertEqual(expense_deltas(100, 1, [2, 3]), {1: 100, 2: -50, 3: -50})

    def test_payments_only_reduce_existing_net_debt(self):
        balances = {1: 300000, 2: 0, 3: -300000}
        self.assertEqual(payment_deltas(200000, 3, 1, balances), {3: 200000, 1: -200000})
        for sender, receiver, amount in [(3, 1, 300001), (1, 3, 1), (3, 3, 1), (2, 1, 1), (3, 1, 0)]:
            with self.assertRaises(ValueError):
                payment_deltas(amount, sender, receiver, balances)

    def test_random_ledgers_settle_to_exact_zero(self):
        rng = random.Random(42)
        balances = dict.fromkeys(range(1, 26), 0)
        for _ in range(200):
            members = rng.sample(list(balances), rng.randint(1, 25))
            amount = rng.randint(1, 10000000)
            deltas = expense_deltas(amount, rng.choice(list(balances)), members)
            self.assertEqual(sum(deltas.values()), 0)
            for uid, delta in deltas.items():
                balances[uid] += delta
            simulated = balances.copy()
            transfers = settlements(balances)
            for sender, recipient, value in transfers:
                for uid, delta in payment_deltas(value, sender, recipient, simulated).items():
                    simulated[uid] += delta
            self.assertTrue(all(value == 0 for value in simulated.values()))
            self.assertLessEqual(len(transfers), 24)
