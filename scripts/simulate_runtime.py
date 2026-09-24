"""Deterministic progression smoke study using the actual production transitions.

Models 4-5 active days/week, 300-500 raw social XP on active days, three
visits with automation only in the simulated player's decision policy.
The bot itself never automatically crafts or breaks through for users.
"""
import argparse
import copy
import json
import random
import statistics
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.cultivation import engine as E, rules as R


def simulate(seed, days=240, active=.642857142857, cap_profile=False):
    rng = random.Random(seed)
    s = E.initial()
    start = 1800000000//86400*86400
    p = E.player(s, 1, 'Simulation', start, rng)
    milestones, metrics = {}, Counter()
    serial = 0
    def action(op, now, **args):
        nonlocal s, p, serial
        serial += 1
        # Match store transaction rollback on failed commands.
        before = copy.deepcopy(s)
        try:
            text = E.execute(s, 1, op, args, now, rng, str(serial))
            metrics[op] += 1
            if op == 'breakthrough' and p['realm'] and p['realm'] not in milestones:
                milestones[p['realm']] = round((now-start)/86400, 3)
            return text
        except E.GameError:
            s = before
            p = s['players']['1']
            return None
    for day in range(days):
        now = start+day*86400+4*3600
        E.settle(s, now)
        if rng.random() > active:
            continue
        raw = 1800 if cap_profile else rng.randint(300, 500)
        explore_count = 3 if cap_profile else rng.randint(1, 2)
        hunts = 5 if cap_profile else 2
        dungeons = 2 if cap_profile else 1
        # Twelve short interaction points across the active day. XP delivered
        # in small chunks; real activity may differ, particularly at tier caps.
        for visit in range(12):
            now = start+day*86400+4*3600+visit*1800
            E.settle(s, now)
            E.xp(p, raw/12, now, social=True)
            if p['event']:
                action('event', now, choice='inspect')
            # Use the free reroll UI only once; no best-of-infinite optimization.
            if p['realm'] >= 4:
                return milestones, metrics, p['coins']
            r = p['realm']
            target = 'minor' if p['tier'] < 8 else 'major'
            need = R.MINOR_COST[p['tier']] if target == 'minor' else 1
            # Craft needed advancement pills ahead of full XP, no automatic gifts.
            if E.bag(p, target)+E.bag(p, target, quality='fine') < need and not E.running(s, '1', 'craft'):
                recipe = R.RECIPES[target]
                for mat, amount in recipe['materials'].items():
                    missing = max(0, amount-E.bag(p, mat))
                    if mat in R.SHOP and missing:
                        action('buy', now, item=mat, count=min(10, missing))
                action('craft', now, item=target, count=1)
            if p['xp'] >= R.cap(p) and not E.running(s, '1'):
                action('breakthrough', now)
            if visit < explore_count:
                area = 'herb' if E.bag(p, 'herb') < E.bag(p, 'water')*2 else 'water'
                action('explore', now, area=area)
            if not E.running(s, '1', 'combat'):
                p['potions'] = min(1, E.bag(p, 'heal')+E.bag(p, 'heal', quality='fine'))
                if visit < dungeons:
                    action('dungeon', now)
                elif visit < dungeons+hunts:
                    action('hunt', now)
            if visit == 8 and not E.running(s, '1', 'craft') and E.bag(p, 'heal') < 1:
                action('craft', now, item='heal', count=1)
        E.settle(s, now+7200)
        if p['xp'] >= R.cap(p) and not E.running(s, '1') and p['realm'] < 4:
            action('breakthrough', now+7200)
    return milestones, metrics, p['coins']


def study(n, days):
    samples = [simulate(i, days) for i in range(n)]
    realms = {}
    for index in range(1, 5):
        values = sorted(x[0][index] for x in samples if index in x[0])
        realms[R.REALMS[index]] = {'reached': len(values), 'total': n,
            'mean_days': round(statistics.mean(values), 2) if values else None,
            'p10': values[int((len(values)-1)*.1)] if values else None,
            'p90': values[int((len(values)-1)*.9)] if values else None}
    return {'version': R.VERSION, 'seed_range': [0,n-1], 'horizon': days, 'realms': realms,
            'mean_final_coins': round(statistics.mean(x[2] for x in samples), 2)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=int, default=100)
    parser.add_argument('--days', type=int, default=240)
    parser.add_argument('--output')
    args = parser.parse_args()
    result = study(args.samples, args.days)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text+'\n')
    print(text)
