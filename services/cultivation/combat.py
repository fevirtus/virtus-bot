"""Deterministic auto combat; output is persisted before the timer starts."""
import random


def battle(players, realm, kind, seed):
    rng = random.Random(seed)
    fighters = []
    roots = ['Kim', 'Mộc', 'Thổ', 'Thủy', 'Hỏa']
    enemy_root = rng.randrange(5)
    for user, p in players:
        scale = 2**p['realm'] * (1 + .07*p['tier'])
        s = p['genetics']['stats']
        role = p.get('path', 'novice') if p['realm'] else 'novice'
        hp, atk = 240*scale*s['hp']/100, 30*scale*s['attack']/100
        talents = p['genetics']['talents']
        hp *= 1.04 if 'Kiên Cường' in talents else 1
        root = roots.index(p['genetics']['root'])
        atk *= 1.05 if (root+1)%5 == enemy_root else (.95 if (enemy_root+1)%5 == root else 1)
        if role == 'body':
            hp *= 1.25
            atk *= .85
        if role == 'sword':
            atk *= 1.15
        strategy = p.get('strategy', 'balanced')
        if strategy == 'attack':
            atk *= 1.15
        if strategy == 'careful':
            atk *= .9
        if p.get('_injured'):
            atk *= .8
        fighters.append({'id': user, 'hp': hp, 'max': hp, 'atk': atk, 'scale': scale,
                         'defense': 12*scale*s['defense']/100, 'shield': p.get('_shield', 0),
                         'mana': 80*s['mana']/100*(1.1 if 'Linh Hải' in talents else 1)*(1+p.get('_focus', 0)), 'defiant': 'Nghịch Thiên' in talents, 'role': role, 'strategy': strategy,
                         'crit': .17 if 'Kiếm Tâm' in p['genetics']['talents'] else .12,
                         'budget': p.get('_potions', 0), 'fine': p.get('_fine_potions', 0), 'used': 0, 'damage': 0, 'support': 0})
        fighters[-1]['hp'] *= p.get('_health', 1)
        fighters[-1]['mana'] = p.get('_mana', fighters[-1]['mana'])
    # Choose difficulty from the strongest participant; no cheap high-level carry.
    scale = 2**realm*(1+.035*max(p['tier'] for _, p in players))
    boss = kind != 'hunt'
    hp = (390 if boss else 155)*scale*(1+.78*(len(fighters)-1))
    total_hp = hp
    enemy_attack = (22 if boss else 20)*scale
    log = []
    won = False
    for tick in range(1, 31 if boss else 16):
        alive = [f for f in fighters if f['hp'] > 0]
        if not alive:
            break
        rng.shuffle(alive)
        for f in alive:
            if f['hp'] < .3*f['max'] and f['used'] < f['budget']:
                healing = .55 if f['used'] >= f['budget']-f['fine'] else .45
                f['used'] += 1
                f['hp'] = min(f['max'], f['hp']+healing*f['max'])
            factor = 1.04 if f['defiant'] and f['hp'] < .3*f['max'] else 1
            if tick % 3 == 0 and f['mana'] >= 15:
                f['mana'] -= 15
                factor = 1.04 if f['defiant'] and f['hp'] < .3*f['max'] else 1.75
                if f['role'] == 'mage':
                    target = min(alive, key=lambda a: a['hp']/a['max'])
                    healed = min(target['max']-target['hp'], .16*target['max'])
                    target['hp'] += healed
                    f['support'] += healed
                    factor = 1.04 if f['defiant'] and f['hp'] < .3*f['max'] else 1.1
            hit = f['atk']*factor*rng.uniform(.9, 1.1)*100/113
            if rng.random() < f['crit']:
                hit *= 1.5
            hp -= hit
            f['damage'] += hit
            if hp <= 0:
                won = True
                break
        if won:
            break
        targets = alive if boss and tick % 4 == 0 else [rng.choice(alive)]
        guardian = next((f for f in alive if f['role'] == 'body'), None)
        for f in targets:
            hit = enemy_attack*rng.uniform(.85, 1.2)*100/(100+f['defense']/f['scale'])
            if len(targets) > 1:
                hit *= .65
            if rng.random() < .1:
                hit *= 1.5
            if f['strategy'] == 'careful':
                hit *= .8
            if f['strategy'] == 'attack':
                hit *= 1.15
            hit *= 1-f['shield']
            if guardian and guardian is not f:
                guardian['support'] += hit*.15
                hit *= .85
            f['hp'] = max(0, f['hp']-hit)
        if tick % 4 == 0:
            log.append(f"Nhịp {tick}: đối thủ còn {max(0, round(hp/total_hp*100))}% sinh lực.")
    return {'won': won, 'seconds': max(30, tick*7), 'log': log[-4:],
            'participants': {f['id']: {'used': f['used'], 'damage': round(f['damage']),
                                      'support': round(f['support']), 'health': f['hp']/f['max'], 'mana': f['mana']} for f in fighters}}
