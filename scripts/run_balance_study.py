"""Reproduce sensitivity tests and matched-seed standalone combat experiments."""
import argparse
import copy
import json
import random
from pathlib import Path

from simulate_game_balance import fight, simulate

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, default=ROOT/'docs/game/balance/candidate-004.json')
    p.add_argument('--samples', type=int, default=500)
    args = p.parse_args()
    c = json.loads(args.config.read_text())
    suffix = c['version'].split('-')[-1]
    folder = args.config.parent
    sensitivity = {}
    for name, changes in [('baseline', {}), ('no_shop', {'shop_enabled': False}),
                          ('no_potions', {'potions_enabled': False}),
                          ('expensive_shop', {'shop_prices': {'herb': 8, 'water': 10}})]:
        candidate = copy.deepcopy(c)
        candidate['realms'] = candidate['realms'][:1]
        candidate['horizon_days'] = 90
        candidate.update(changes)
        sensitivity[name] = simulate(candidate, args.samples, ['moderate'])
        print(name, sensitivity[name]['profiles']['moderate']['milestones']['Truc Co']['days_cumulative'], flush=True)
    (folder/f'sensitivity-{suffix}.json').write_text(json.dumps(sensitivity, indent=2)+'\n')
    rows = []
    for realm in (0, 1):
        for party in (1, 3):
            for strategy in ('attack', 'balanced', 'careful'):
                for budget in (0, 1, 2):
                    for injury in (False, True):
                        runs = [fight(random.Random(400000+i), c, realm, 4, 'boss', party,
                                      strategy, injury, budget, 1) for i in range(args.samples)]
                        rows.append({'realm_index': realm, 'party': party, 'strategy': strategy,
                                     'injured': injury, 'potion_budget': budget, 'samples': args.samples,
                                     'win_percent': round(100*sum(r[0] for r in runs)/len(runs), 2),
                                     'mean_seconds': round(sum(r[1] for r in runs)/len(runs), 2),
                                     'mean_potions_used': round(sum(r[2] for r in runs)/len(runs), 3)})
    (folder/f'combat-{suffix}.json').write_text(json.dumps(rows, indent=2)+'\n')
    print(f'Combat study: {len(rows)} scenarios x {args.samples} battles.', flush=True)


if __name__ == '__main__':
    main()
