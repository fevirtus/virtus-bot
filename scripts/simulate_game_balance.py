"""Event-driven offline balance lab; standard library, no Discord/DB access.

All candidate formulas are hypotheses, not production rules. See balance report.
"""
import argparse
import heapq
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def percentile(values, fraction):
    return round(sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)], 2) if values else None


def describe(values):
    return {'n': len(values), 'mean': round(statistics.mean(values), 2) if values else None,
            'p10': percentile(values, .1), 'p50': percentile(values, .5),
            'p90': percentile(values, .9)}


def fight(rng, c, realm, tier, mode, party, strategy, injured, potions, quality):
    """Actual HP/mana/damage simulation, not a sampled win probability.

    Allies have equal progression; damage/heal/guard all affect survival.
    Potions belong only to focal player. Allies use no inventory potions.
    """
    tune = c['combat']
    scale = c['realms'][realm]['power'] * (1 + .07 * tier)
    members = []
    for i in range(party):
        role = ('sword', 'body', 'mage')[i % 3] if realm else 'novice'
        hp = 240 * scale * (2 - quality)
        atk = 30 * scale * quality
        defense = 12 * scale
        if role == 'body':
            hp *= 1.25
            atk *= .85
        elif role == 'sword':
            atk *= 1.15
        if strategy == 'attack':
            atk *= 1.15
            defense *= .8
        elif strategy == 'careful':
            atk *= .9
            defense *= 1.2
        if injured and i == 0:
            atk *= .8
        members.append({'hp': hp, 'max': hp, 'atk': atk, 'def': defense,
                        'mana': 80, 'role': role})
    nscale = 1 + .78 * (party - 1)
    boss = mode == 'boss'
    ehp = (tune['boss_hp'] if boss else tune['hunt_hp']) * scale * nscale
    eatk = (tune['boss_attack'] if boss else tune['hunt_attack']) * scale
    edef = (13 if boss else 8) * scale
    consumed, dealt, supported = 0, 0.0, 0.0
    limit = tune['boss_ticks'] if boss else tune['hunt_ticks']
    for tick in range(1, limit + 1):
        alive = [m for m in members if m['hp'] > 0]
        if not alive:
            return False, tick * tune['seconds_per_tick'], consumed, dealt, supported
        order = list(alive)
        rng.shuffle(order)
        weak = min(alive, key=lambda m: m['hp']/m['max'])
        for m in order:
            if m is members[0] and 0 < m['hp'] < .3*m['max'] and consumed < potions:
                m['hp'] = min(m['max'], m['hp'] + .45*m['max'])
                consumed += 1
            multiplier = 1.0
            if tick % 3 == 0 and m['mana'] >= 15:
                m['mana'] -= 15
                if m['role'] == 'mage':
                    heal = min(weak['max']-weak['hp'], .16*weak['max'])
                    weak['hp'] += heal
                    supported += heal
                    multiplier = 1.1
                else:
                    multiplier = 1.75
            damage = m['atk']*multiplier*rng.uniform(.9, 1.1)*(100*scale)/(100*scale+edef)
            if rng.random() < .12:
                damage *= 1.5
            ehp -= damage
            dealt += damage
            if ehp <= 0:
                return True, tick*tune['seconds_per_tick'], consumed, dealt, supported
        alive = [m for m in members if m['hp'] > 0]
        if not alive:
            break
        # Boss telegraph/aoe phases, variable targeting and crit; guard helps team.
        targets = alive if boss and tick % 4 == 0 else [rng.choice(alive)]
        guarded = any(m['role'] == 'body' for m in alive)
        for m in targets:
            damage = eatk*rng.uniform(.85, 1.2)*(100*scale)/(100*scale+m['def'])
            if len(targets) > 1:
                damage *= .65
            if rng.random() < .10:
                damage *= 1.5
            if guarded and m['role'] != 'body':
                supported += damage*.15
                damage *= .85
            if strategy == 'careful':
                damage *= tune.get('careful_damage_taken', 1.0)
            elif strategy == 'attack':
                damage *= tune.get('attack_damage_taken', 1.0)
            m['hp'] = max(0, m['hp']-damage)
    return False, limit*tune['seconds_per_tick'], consumed, dealt, supported


class Player:
    def __init__(self, c, profile, seed):
        self.c, self.profile = c, profile
        self.schedule_rng = random.Random(seed)
        self.combat_rng = random.Random(seed + 10000000)
        self.loot_rng = random.Random(seed + 20000000)
        self.progress_rng = random.Random(seed + 30000000)
        self.queue, self.sequence = [], 0
        self.realm, self.tier, self.xp = 0, 0, 0.0
        self.coins = c['initial_coins']
        self.stock = [Counter() for _ in c['realms']]
        self.craft_streak, self.insight = Counter(), Counter()
        self.metrics, self.blocked = Counter(), Counter()
        self.milestones, self.snapshots = [], []
        self.injured_until = -1
        self.crafting = False
        self.day_social, self.shop_bought = Counter(), Counter()
        self.finished = False
        self.quality = self.schedule_rng.uniform(.95, 1.05)
        self.shop = c.get('shop_enabled', True)
        self.prepare_schedule()

    def add(self, time, event, data=None):
        self.sequence += 1
        heapq.heappush(self.queue, (time, self.sequence, event, data))

    def prepare_schedule(self):
        p = self.profile
        for day in range(self.c['horizon_days']):
            if day and self.schedule_rng.random() >= p['active_probability']:
                continue
            # Model day is a 04:00 reset day. Spread rewards over a 4-hour visit.
            start = day*1440 + self.schedule_rng.uniform(480, 600)
            raw = self.schedule_rng.randint(*p['raw_social_xp'])
            for j in range(24):
                self.add(start+j*10, 'social', (day, raw/24))
            explorations = self.schedule_rng.randint(*p['explore'])
            for j in range(explorations):
                self.add(start+20*j, 'explore_start')
            modes = ['hunt']*p['hunt'] + ['dungeon']*p['dungeon']
            self.add(start+5, 'outing', modes)

    def earn(self, value, source):
        self.coins += value
        self.metrics['income_'+source] += value

    def spend(self, value, source):
        assert value >= 0 and self.coins >= value
        self.coins -= value
        self.metrics['spent_'+source] += value

    def gain_xp(self, amount, now):
        if now < self.injured_until:
            self.metrics['injured_xp_lost'] += amount*.5
            amount *= .5
        cap = self.c['realms'][self.realm]['xp'][self.tier]
        accepted = min(amount, cap-self.xp)
        self.metrics['xp_wasted_at_cap'] += amount-accepted
        self.metrics['xp_earned'] += accepted
        self.xp += accepted

    def reward(self, mode, now, r):
        cfg = self.c['realms'][r]
        self.earn(cfg['rewards'][mode]['coins'], mode)
        # Combat cannot change realm mid-outing in this model; rewards stay bound.
        if r == self.realm:
            self.gain_xp(cfg['rewards'][mode]['xp'], now)
        stock = self.stock[r]
        if mode == 'boss':
            stock['core'] += 1
            self.metrics['gathered_core'] += 1
            stock['fragment'] += 1
            if self.loot_rng.random() < self.c['whole_relic_drop']:
                stock['relic'] += 1
            stock['relic'] += stock['fragment']//5
            stock['fragment'] %= 5
        elif mode == 'hunt':
            stock['blood'] += 1
        self.metrics['rewards_'+mode] += 1

    def recipe(self, kind):
        cfg = self.c['realms'][self.realm]
        result = dict(self.c['recipes'][kind])
        result['coins'] = round(result['coins']*cfg['cost_scale'])
        return result

    def procure(self, recipe, now):
        stock = self.stock[self.realm]
        day = int(now//1440)
        missing = {k: max(0, v-stock[k]) for k, v in recipe.items() if k != 'coins'}
        if any(n and k not in self.c['shop_prices'] for k, n in missing.items()):
            self.blocked['special_materials'] += 1
            return False
        count = sum(missing.values())
        price = sum(n*self.c['shop_prices'].get(k, 0) for k, n in missing.items())
        if count and (not self.shop or count+self.shop_bought[day] > self.c['shop_daily_units']):
            self.blocked['shop_limit_or_disabled'] += 1
            return False
        if self.coins < recipe['coins']+price:
            self.blocked['coins'] += 1
            return False
        if count:
            self.spend(price, 'shop')
            self.shop_bought[day] += count
            for k, n in missing.items():
                stock[k] += n
                self.metrics['bought_'+k] += n
        return True

    def start_craft(self, kind, now):
        recipe = self.recipe(kind)
        if not self.procure(recipe, now):
            return False
        self.spend(recipe['coins'], 'craft')
        for k, v in recipe.items():
            if k != 'coins':
                self.stock[self.realm][k] -= v
                self.metrics['consumed_'+k] += v
        self.crafting = True
        self.add(now+self.c['craft_minutes'][kind], 'crafted', (self.realm, kind, recipe))
        return True

    def progress(self, now, allow_start=True):
        if self.finished:
            return
        cfg, stock = self.c['realms'][self.realm], self.stock[self.realm]
        full = self.xp >= cfg['xp'][self.tier]-1e-8
        if full and now >= self.injured_until:
            if self.tier < 8:
                required = self.c['minor_pills'][self.tier]
                if stock['minor'] >= required:
                    stock['minor'] -= required
                    self.xp, self.tier = 0, self.tier+1
                    self.metrics['minor_breakthroughs'] += 1
                    full = False
            elif stock['major'] and stock['relic'] and self.coins >= cfg['ritual_coins']:
                stock['major'] -= 1
                stock['relic'] -= 1
                self.spend(cfg['ritual_coins'], 'ritual')
                chance = min(1, cfg['break_base']+self.insight[self.realm]*cfg['insight'])
                self.metrics['break_attempts'] += 1
                if self.progress_rng.random() < chance:
                    self.milestones.append(now/1440)
                    self.metrics['inventory_herb_at_milestone'] = stock['herb']
                    self.metrics['inventory_water_at_milestone'] = stock['water']
                    self.metrics['inventory_core_at_milestone'] = stock['core']
                    self.snapshots.append(dict(self.metrics, coins=self.coins))
                    self.realm += 1
                    if self.realm == len(self.c['realms']):
                        self.finished = True
                        return
                    self.tier, self.xp = 0, 0.0
                    cfg, stock = self.c['realms'][self.realm], self.stock[self.realm]
                else:
                    self.insight[self.realm] += 1
                    self.metrics['break_failures'] += 1
                    self.xp -= cfg['xp'][8]*.1
                    self.injured_until = now+cfg['injury_hours']*60
            elif full:
                self.blocked['ritual_requirements'] += 1
        if self.crafting or not allow_start:
            return
        if self.tier < 8:
            # Prepare the next small breakthrough only, one furnace, no free pills.
            if stock['minor'] < self.c['minor_pills'][self.tier]:
                self.start_craft('minor', now)
        elif not stock['major']:
            self.start_craft('major', now)
        if not self.crafting and self.c.get('potions_enabled', True):
            # Optional player policy: preserve ritual reserve before healing stock.
            if stock['heal'] < 2 and self.coins >= cfg['ritual_coins']+40:
                self.start_craft('heal', now)

    def run(self):
        self.busy = False
        while self.queue and not self.finished:
            now, _, event, data = heapq.heappop(self.queue)
            if now >= self.c['horizon_days']*1440:
                break
            stock = self.stock[self.realm]
            if event == 'social':
                day, raw = data
                # Injury applies before accepted XP consumes the shared social cap.
                raw *= .5 if now < self.injured_until else 1
                current = self.day_social[day]
                full = min(raw, max(0, 600-current))
                value = min(900-current, full+(raw-full)*.25)
                self.day_social[day] += value
                # Already injury-adjusted; preserve the XP function's contract.
                saved = self.injured_until
                self.injured_until = -1
                self.gain_xp(value, now)
                self.injured_until = saved
                self.metrics['social_xp'] += value
                # Proposed limited social ingredient milestone; no currency faucet.
                if current < 200 <= self.day_social[day]:
                    stock['herb'] += 2
                    stock['water'] += 1
                    self.metrics['social_material_grants'] += 1
                    self.metrics['gathered_herb'] += 2
                    self.metrics['gathered_water'] += 1
            elif event == 'explore_start':
                self.add(now+20, 'explore', self.realm)
            elif event == 'explore':
                stock = self.stock[data]
                # Targeted farming guarantees basics; random extra herb.
                herbs = 3+self.loot_rng.randint(0, 2)
                stock['herb'] += herbs
                stock['water'] += 2
                self.metrics['gathered_herb'] += herbs
                self.metrics['gathered_water'] += 2
                self.reward('explore', now, data)
            elif event == 'outing':
                if data:
                    self.busy = True
                    mode, remaining = data[0], data[1:]
                    r = self.realm
                    party = self.profile.get('party', 1) if mode == 'dungeon' else 1
                    stages = ['hunt', 'boss'] if mode == 'dungeon' else ['hunt']
                    self.add(now, 'fight', (r, party, stages, remaining, False, 2))
                else:
                    self.busy = False
            elif event == 'fight':
                r, party, stages, remaining, slot_spent, allowance = data
                mode = stages[0]
                budget = min(allowance, self.stock[r]['heal']) if self.c.get('potions_enabled', True) else 0
                self.stock[r]['heal'] -= budget
                win, seconds, used, damage, support = fight(
                    self.combat_rng, self.c, r, self.tier, mode, party,
                    self.profile.get('strategy', 'balanced'), now < self.injured_until,
                    budget, self.quality)
                self.metrics[mode+'_attempts'] += 1
                self.metrics[mode+'_wins'] += int(win)
                self.metrics[mode+'_seconds'] += seconds
                assert used <= budget <= allowance
                self.metrics['potions_used'] += used
                self.metrics['damage'] += damage
                self.metrics['support'] += support
                self.add(now+seconds/60, 'fought', (r, party, stages, remaining, win, budget-used, slot_spent, allowance-used))
            elif event == 'fought':
                r, party, stages, remaining, win, unused, spent, allowance = data
                self.stock[r]['heal'] += unused
                if win:
                    self.reward(stages[0], now, r)
                    if not spent:
                        self.metrics['reward_slots'] += 1
                    if len(stages) > 1:
                        # Event is skipped safely in offline policy; no free event loot.
                        self.add(now+self.c['combat']['dungeon_transition_seconds']/60, 'fight', (r, party, stages[1:], remaining, True, allowance))
                    else:
                        self.add(now+1, 'outing', remaining)
                else:
                    self.add(now+1, 'outing', remaining)
                # Busy remains true until this outing sequence ends.
            elif event == 'crafted':
                r, kind, recipe = data
                key = (r, kind)
                success = (kind != 'major' or self.craft_streak[key] >= 2
                           or self.progress_rng.random() < self.c['realms'][r]['craft_success'])
                self.metrics['crafted_'+kind] += int(success)
                if success:
                    self.stock[r][kind] += 1
                    self.craft_streak[key] = 0
                else:
                    self.craft_streak[key] += 1
                    self.metrics['craft_failures'] += 1
                    for k, v in recipe.items():
                        if k != 'coins':
                            self.stock[r][k] += v//2
                            self.metrics['refunded_'+k] += v//2
                self.crafting = False
            # Policy checks around real activity/XP events, not once per day.
            # No new actions from craft completion alone (not an unattended auto-loop).
            if not self.busy:
                self.progress(now, allow_start=event != 'crafted')
            assert self.coins >= 0 and all(v >= 0 for bag in self.stock for v in bag.values())
            income = sum(v for k, v in self.metrics.items() if k.startswith('income_'))
            spent = sum(v for k, v in self.metrics.items() if k.startswith('spent_'))
            assert abs(self.coins - (self.c['initial_coins'] + income - spent)) < 1e-6
        return {'milestones': self.milestones, 'snapshots': self.snapshots,
                'metrics': dict(self.metrics), 'blocked': dict(self.blocked),
                'final_coins': self.coins, 'realm': self.realm, 'tier': self.tier,
                'stock': [dict(s) for s in self.stock]}


def simulate(c, samples=None, profiles=None):
    n = samples or c['samples']
    result = {'version': c['version'], 'seed': c['seed'], 'samples': n,
              'horizon_days': c['horizon_days'], 'profiles': {}}
    for idx, (name, p) in enumerate(c['profiles'].items()):
        if profiles and name not in profiles:
            continue
        rows = [Player(c, p, c['seed']+idx*100000+i).run() for i in range(n)]
        realm_data = {}
        for r, cfg in enumerate(c['realms']):
            done = [row for row in rows if len(row['milestones']) > r]
            days = [row['milestones'][r] for row in done]
            transitions = [row['milestones'][r]-(row['milestones'][r-1] if r else 0) for row in done]
            metrics = Counter()
            for row in done:
                metrics.update(row['snapshots'][r])
            mean_metrics = {k: round(v/len(done), 3) for k, v in metrics.items()} if done else {}
            realm_data[cfg['target']] = {'completed_percent': round(100*len(done)/n, 2),
                'days_cumulative': describe(days), 'days_in_realm': describe(transitions),
                'by_day_10_percent': round(100*sum(d <= 10 for d in days)/n, 2),
                'mean_cumulative_metrics_at_completion': mean_metrics}
        totals = Counter()
        for row in rows:
            totals.update(row['metrics'])
        result['profiles'][name] = {'milestones': realm_data,
            'combat': {mode: {'attempts': totals[mode+'_attempts'],
                'win_percent': round(100*totals[mode+'_wins']/max(1, totals[mode+'_attempts']), 2),
                'mean_seconds': round(totals[mode+'_seconds']/max(1, totals[mode+'_attempts']), 2)}
                for mode in ('hunt', 'boss')},
            'mean_final_coins': round(statistics.mean(row['final_coins'] for row in rows), 2),
            'blocked_checks': dict(sum((Counter(row['blocked']) for row in rows), Counter()))}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT/'docs/game/balance/candidate-004.json')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/game/balance/result-004.json')
    parser.add_argument('--samples', type=int)
    parser.add_argument('--profiles', nargs='+')
    args = parser.parse_args()
    c = json.loads(args.config.read_text())
    result = simulate(c, args.samples, args.profiles)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    for name, data in result['profiles'].items():
        print(name, {k: v['days_cumulative'] for k, v in data['milestones'].items()}, data['combat'])


if __name__ == '__main__':
    main()
