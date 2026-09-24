"""Offline first-realm economy model. Assumptions are documented in the report.

Python standard library only; never connects to Discord or the production DB.
Run: python3 scripts/simulate_progression.py
"""
import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def affordable(stock, recipe):
    return all(stock[k] >= amount for k, amount in recipe.items())


def run_player(c, profile, rng):
    stock = Counter(coins=c['initial_coins'])
    tier, xp, fragments, relics = 0, 0.0, 0, 0
    pills, craft_fails, break_fails = 0, 0, 0
    injured_until = -1.0
    failures = Counter()
    blocked = Counter()
    for day in range(c['horizon_days']):
        if day and rng.random() >= profile['active_probability']:
            continue
        # One visit on each active day; day zero is the first login.
        now = day * 24 + rng.uniform(6, 22)
        incoming = rng.randint(*profile['social_xp'])
        for _ in range(rng.randint(*profile['explore'])):
            for k, v in c['explore'].items():
                if k == 'xp':
                    incoming += v
                else:
                    stock[k] += v
            now += 20 / 60
        for _ in range(profile['hunt']):
            stock['coins'] += c['hunt']['coins']
            incoming += c['hunt']['xp']
        for _ in range(profile['boss']):
            if rng.random() < c['boss_win']:
                for k, v in c['boss'].items():
                    if k == 'xp':
                        incoming += v
                    else:
                        stock[k] += v
                fragments += 1
                if rng.random() < c['boss_whole_drop']:
                    relics += 1
        relics += fragments // c['boss_fragments_needed']
        fragments %= c['boss_fragments_needed']
        if now < injured_until:
            incoming *= c['injury_xp_multiplier']
        # Conservative visit model: current tier cap; no unapproved XP reservoir.
        xp = min(c['tier_xp'][tier], xp + incoming)
        if tier < 8:
            recipe = {k: v * c['minor_pills'][tier]
                      for k, v in c['minor_recipe'].items()}
            if xp >= c['tier_xp'][tier]:
                if affordable(stock, recipe):
                    for k, v in recipe.items():
                        stock[k] -= v
                    now += c['minor_minutes'] * c['minor_pills'][tier] / 60
                    tier += 1
                    xp = 0.0
                else:
                    blocked['minor_materials_or_coins'] += 1
            continue
        # Prepare a major pill while filling the final tier. One attempt/visit.
        if pills == 0:
            recipe = c['major_recipe']
            if affordable(stock, recipe):
                for k, v in recipe.items():
                    stock[k] -= v
                now += c['major_minutes'] / 60
                if (craft_fails >= c['craft_guaranteed_after_failures']
                        or rng.random() < c['craft_success']):
                    pills += 1
                    craft_fails = 0
                else:
                    failures['craft'] += 1
                    craft_fails += 1
                    for k, v in recipe.items():
                        if k != 'coins':
                            stock[k] += v // 2
            else:
                blocked['major_materials_or_coins'] += 1
        if xp < c['tier_xp'][8]:
            blocked['final_tier_xp'] += 1
            continue
        if not pills or not relics or stock['coins'] < c['ritual_coins']:
            blocked['ritual_resources'] += 1
            continue
        if now < injured_until:
            blocked['injury'] += 1
            continue
        pills -= 1
        relics -= 1
        stock['coins'] -= c['ritual_coins']
        chance = min(1, c['breakthrough_base'] + break_fails * c['insight_increment'])
        if rng.random() < chance:
            assert min(stock.values(), default=0) >= 0
            assert break_fails <= 4
            return {'day': now / 24, 'failures': dict(failures),
                    'blocked': dict(blocked), 'coins': stock['coins']}
        failures['breakthrough'] += 1
        break_fails += 1
        xp -= c['tier_xp'][8] * c['failure_xp_fraction']
        injured_until = now + c['injury_hours']
    return {'day': None, 'failures': dict(failures), 'blocked': dict(blocked),
            'coins': stock['coins']}


def quantile(values, p):
    return round(sorted(values)[max(0, math.ceil(len(values) * p) - 1)], 2) if values else None


def simulate(c):
    results = {}
    for index, (name, profile) in enumerate(c['profiles'].items()):
        runs = [run_player(c, profile, random.Random(c['seed'] + index * 100000 + i))
                for i in range(c['samples_per_profile'])]
        days = [r['day'] for r in runs if r['day'] is not None]
        results[name] = {
            'completed': len(days), 'samples': len(runs),
            'completion_percent': round(100 * len(days) / len(runs), 2),
            'days_p10': quantile(days, .1), 'days_p50': quantile(days, .5),
            'days_p90': quantile(days, .9),
            'by_day_21_percent': round(100 * sum(d <= 21 for d in days) / len(runs), 2),
            'mean_craft_failures': round(sum(r['failures'].get('craft', 0) for r in runs)/len(runs), 3),
            'mean_breakthrough_failures': round(sum(r['failures'].get('breakthrough', 0) for r in runs)/len(runs), 3),
            'blocked_visits': dict(sum((Counter(r['blocked']) for r in runs), Counter()))
        }
    return {'config': c['version'], 'seed': c['seed'], 'horizon_days': c['horizon_days'],
            'note': 'Quantiles conditional on completion; days since first login. See model limitations.',
            'results': results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT/'docs/game/balance/candidate-001.json')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/game/balance/result-001.json')
    args = parser.parse_args()
    c = json.loads(args.config.read_text())
    assert len(c['tier_xp']) == 9 and len(c['minor_pills']) == 8
    assert all(x > 0 for x in c['tier_xp'])
    result = simulate(c)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
