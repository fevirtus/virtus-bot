"""Pure state transitions; callers must serialize a guild and persist atomically."""
import copy
import random
from collections import Counter

from . import rules as R
from .combat import battle


class GameError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GameError(message)


def initial():
    return {'version': R.VERSION, 'players': {}, 'jobs': {}, 'rooms': {}, 'outbox': {},
            'sect': {'buildings': {k: 0 for k in R.BUILDINGS}, 'fund': 0, 'votes': {},
                     'week': '', 'progress': 0, 'boss_damage': 0, 'boss_claimed': []}}


def upgrade_state(state, now):
    state.setdefault('outbox', {})
    state.setdefault('notice_seq', 0)
    for p in state['players'].values():
        p.setdefault('recipes', [])
        p.setdefault('inbox_seq', 0)
        p.setdefault('chat_hashes', [])
    state['version'] = R.VERSION
    reset_week(state, now)


def reset_week(state, now):
    sect = state['sect']
    week = R.week_key(now)
    if sect['week'] < week:
        sect.update(week=week, progress=0, boss_damage=0, boss_claimed=[], boss_members=[], votes={},
                    boss_target=0)


def notice(state, kind, user, text, now):
    state['notice_seq'] = state.get('notice_seq', 0)+1
    key = str(state['notice_seq'])
    state.setdefault('outbox', {})[key] = {'kind': kind, 'user': str(user), 'text': text,
                                         'created': now, 'status': 'pending'}


def boss_target(state):
    sect = state['sect']
    if not sect.get('boss_target'):
        active = sum(p['active'] for p in state['players'].values())
        sect['boss_target'] = max(600, min(10000, active*500))
    return sect['boss_target']


def player(state, user, name, now, rng):
    user = str(user)
    if user not in state['players']:
        state['players'][user] = {
            'name': name[:80], 'realm': 0, 'tier': 0, 'xp': 0, 'coins': 150,
            'inventory': {}, 'genetics': R.stats_roll(rng), 'roll_locked': False,
            'recipes': [], 'chat_hashes': [], 'candidate': None, 'path': 'sword', 'path_changes': 0, 'strategy': 'balanced',
            'potions': 0, 'active': True, 'notifications': False, 'daily': {}, 'inbox': [],
            'last_chat': 0, 'last_content': '', 'last_content_time': 0,
            'injury_until': 0, 'injury_start': 0, 'injury_shortened': False,
            'insight': 0, 'craft_pity': {}, 'profession_xp': 0,
            'contribution': 0, 'week_points': {}, 'activity_points': {}, 'event': None,
        }
    p = state['players'][user]
    p['name'] = name[:80]
    return p


def bag(p, item, realm=None, quality='normal'):
    return p['inventory'].get(R.item_key(p['realm'] if realm is None else realm, item, quality), 0)


def give(p, item, amount, realm=None, quality='normal'):
    key = R.item_key(p['realm'] if realm is None else realm, item, quality)
    require(p['inventory'].get(key, 0)+amount >= 0, f"Thiếu {R.NAMES.get(item, item)}.")
    p['inventory'][key] = p['inventory'].get(key, 0)+amount


def consume(p, item, amount=1):
    """Use standard stacks first, then superior; return superior count consumed."""
    normal = min(amount, bag(p, item))
    fine = amount-normal
    require(bag(p, item, quality='fine') >= fine, f"Thiếu {R.NAMES[item]}.")
    give(p, item, -normal)
    if fine:
        give(p, item, -fine, quality='fine')
    return fine


def pay(p, amount):
    require(p['coins'] >= amount, f"Cần {amount} linh thạch; hiện có {p['coins']}.")
    p['coins'] -= amount


def inbox(p, text, now):
    p['inbox_seq'] = p.get('inbox_seq', 0)+1
    p['inbox'].append({'id': p['inbox_seq'], 'time': now, 'text': text})
    p['inbox'] = p['inbox'][-30:]


def daily(p, now):
    key = R.day_key(now)
    if p['daily'].get('key') != key:
        p['daily'] = {'key': key, 'social': 0, 'shop': 0}
    return p['daily']


def xp(p, amount, now, social=False, promised=False):
    if not p['active'] and not promised:
        return 0
    amount *= .5 if now < p['injury_until'] else 1
    if social:
        d = daily(p, now)
        previous = d['social']
        full = min(amount, max(0, 600-previous))
        amount = min(max(0, 900-previous), full+(amount-full)*.25)
        d['social'] += amount
        if previous < 200 <= d['social']:
            give(p, 'herb', 2)
            give(p, 'water', 1)
    accepted = min(amount, max(0, R.cap(p)-p['xp']))
    p['xp'] = round(p['xp']+accepted, 2)
    return accepted


def points(state, user, count, now):
    p = state['players'][str(user)]
    week = R.week_key(now)
    p['contribution'] += count
    p['week_points'][week] = p['week_points'].get(week, 0)+count
    p['activity_points'][week] = p['activity_points'].get(week, 0)+1
    for field in ('week_points', 'activity_points'):
        p[field] = {k: p[field][k] for k in sorted(p[field])[-2:]}
    sect = state['sect']
    if sect['week'] > week:
        # Recovery of a previous-week job cannot erase current-week progress.
        sect['fund'] += count
        return
    if sect['week'] != week:
        sect.update(week=week, progress=0, boss_damage=0, boss_claimed=[], boss_members=[], votes={})
    sect['progress'] += count
    sect['fund'] += count


def running(state, user, kind=None):
    return any(str(user) in j['users'] and (kind is None or j['kind'] == kind)
               for j in state['jobs'].values())


def occupied_room(state, user):
    return any(str(user) in room['members'] for room in state['rooms'].values())


def settle(state, now):
    """Settle immutable results exactly once inside the caller's DB transaction."""
    upgrade_state(state, now)
    for jid, job in sorted(list(state['jobs'].items()), key=lambda pair: pair[1]['due']):
        if job['due'] > now:
            continue
        for user in job['users']:
            p = state['players'][user]
            result = job['results'][user]
            p['coins'] += result.get('coins', 0)
            for key, amount in result.get('items', {}).items():
                p['inventory'][key] = p['inventory'].get(key, 0)+amount
            if p['realm'] == job['realm']:
                xp(p, result.get('xp', 0), job['due'], promised=True)
            if job['kind'] == 'craft':
                p['profession_xp'] += result['profession_xp']
                p['craft_pity'][result['recipe_key']] = result['pity']
            if result.get('points'):
                points(state, user, result['points'], job['due'])
            if result.get('boss_damage') and R.week_key(job['due']) == R.week_key(now):
                sect = state['sect']
                if sect['week'] != R.week_key(now):
                    points(state, user, 0, now)
                previous_damage = sect['boss_damage']
                sect['boss_damage'] += result['boss_damage']
                if previous_damage < boss_target(state) <= sect['boss_damage']:
                    notice(state, 'achievement', user, 'Tông môn đã hạ boss tuần! Thành viên đã đóng góp có thể nhận thưởng ở bảng tông môn.', job['due'])
                if user not in sect.setdefault('boss_members', []):
                    sect['boss_members'].append(user)
            if result.get('event') and not p['event']:
                p['event'] = result['event']
            for r in range(len(R.REALMS)):
                fragments = bag(p, 'fragment', r)
                if fragments >= 5:
                    give(p, 'fragment', -(fragments//5)*5, r)
                    give(p, 'relic', fragments//5, r)
            inbox(p, result['message'], job['due'])
            if p['notifications']:
                notice(state, 'private', user, result['message'], job['due'])
        del state['jobs'][jid]
    for rid, room in list(state['rooms'].items()):
        if now >= room['expires']:
            del state['rooms'][rid]
    for p in state['players'].values():
        if p['event'] and now >= p['event']['expires']:
            p['event'] = None


def craft_quote(p, item, count):
    require(item in R.RECIPES and 1 <= count <= 10, "Chọn 1–10 viên và công thức hợp lệ.")
    recipe = R.RECIPES[item]
    return {'coins': recipe['coins']*(p['realm']+1)*count,
            'materials': {k: v*count for k, v in recipe['materials'].items()},
            'seconds': recipe['seconds']*count}


def quote(state, user, op, args):
    p = state['players'][str(user)]
    r = p['realm']
    if op == 'craft':
        q = craft_quote(p, args['item'], args.get('count', 1))
        q['seconds'] = int(q['seconds']*(1-.02*state['sect']['buildings']['alchemy']))
        mats = ', '.join(f"{v} {R.NAMES[k]}" for k, v in q['materials'].items())
        special = args['item'] in ('major', 'reroll')
        rate = min(.95, max(.7, .85-.05*r)+min(.05, p['profession_xp']//100*.01)+(.02 if 'Dược Duyên' in p['genetics']['talents'] else 0)) if special else 1
        refunds = ', '.join(f"{n//2} {R.NAMES[k]}" for k, n in R.RECIPES[args['item']]['materials'].items())
        return f"Luyện {args.get('count', 1)} {R.NAMES[args['item']]}: {mats}; {q['coins']} linh thạch; {q['seconds']//60} phút. Thành công {rate:.0%}; bảo đảm sau 2 lần thất bại cùng công thức. Hoàn khi thất bại mỗi viên: {refunds if special else 'không áp dụng'}; phí không hoàn."
    if op == 'breakthrough':
        if r >= len(R.XP):
            return "Đã đến giới hạn nội dung hiện tại."
        if p['tier'] < 8:
            return f"Dùng {R.MINOR_COST[p['tier']]} Tụ Khí Đan, thành công 100%. Lần đầu kết thúc roll miễn phí vô hạn."
        chance = min(1, [.5, .45, .4, .35][r]+p['insight']*[.15, .125, .1, .1][r]+((.075 if bag(p, 'guard') == 0 and bag(p, 'guard', quality='fine') else .05) if args.get('guard') else 0)+(.025 if bag(p, 'major') == 0 and bag(p, 'major', quality='fine') else 0))
        return f"Dùng 1 đan đại đột phá, 1 linh vật, {80*(r+1)} linh thạch"+(' và 1 Hộ Mạch Đan' if args.get('guard') else '')+f". Thành công {chance:.0%}. Thất bại mất {R.cap(p)*.1:g} tu vi, trọng thương {[6,12,24,24][r]} giờ; vật phẩm/phí đã dùng không hoàn."
    if op == 'roll':
        return (f"Dùng 1 Tẩy Tủy Đan + {200*(r+1)} linh thạch. Xem bộ mới, giữ bộ cũ vẫn mất phí." if p['roll_locked'] else 'Roll miễn phí cả bộ; không giới hạn trước lần đột phá nhỏ đầu tiên.')
    if op == 'buy':
        return f"Mua {args.get('count', 1)} {R.NAMES.get(args['item'], args['item'])}: {R.SHOP.get(args['item'], 0)*args.get('count', 1)} linh thạch."
    if op in ('hunt', 'dungeon', 'sect_boss'):
        return f"Auto combat · {p['strategy']}. Mang tối đa {p['potions']} Hồi Xuân Đan; tự dùng khi HP <30%, trả phần chưa dùng. Phần đã dùng không hoàn. Hết lượt thưởng vẫn chơi được nhưng không nhận thêm XP/vật phẩm."
    if op == 'learn':
        item = args['item']
        require(item in R.RESEARCH, 'Công thức không thể nghiên cứu.')
        return f"Học {R.NAMES[item]} vĩnh viễn: {R.RESEARCH[item]['coins']} linh thạch, Tàng Kinh Các cấp {R.RESEARCH[item]['level']}."
    if op == 'focus':
        return 'Dùng 1 Ngưng Thần Đan đạt chuẩn/thượng phẩm: +10%/+15% mana trận kế tiếp. Không cộng dồn.'
    if op == 'upgrade':
        building = args['building']
        require(building in R.BUILDINGS, 'Công trình không hợp lệ.')
        level = state['sect']['buildings'][building]
        return f"Nâng {R.BUILDINGS[building]} lên cấp {level+1}: {100*(level+1)} điểm quỹ chung."
    if op == 'path':
        return 'Đổi hướng tu luyện: miễn phí lần chọn đầu và một lần đổi; sau đó tốn 5 Linh thảo, chờ 1 giờ giữa các lần trả phí.'
    if op == 'heal_injury':
        return 'Dùng 1 Dưỡng Thương Đan, rút 40% (thượng phẩm 50%) thời gian trọng thương ban đầu; mỗi lần trọng thương chỉ dùng một lần.'
    if op == 'event':
        return 'Dấu tích bí ẩn: quan sát có thể mất tối đa 1 Linh thảo, mở có thể mất tối đa 2; rời đi an toàn. Kết quả chỉ lộ sau lựa chọn.'
    if op == 'donate':
        return f"Hiến {args.get('count', 1)} Linh thảo cho tông môn, không rút lại."
    if op == 'gift':
        return f"Tặng {args.get('count', 1)} {R.NAMES.get(args['item'], args['item'])} ({R.REALMS[args.get('realm', r)]}, {args.get('quality', 'normal')}) cho ID {args['target']}; không hoàn sau xác nhận."
    return 'Xác nhận thực hiện thao tác này?'


def execute(state, user, op, args, now, rng, action_id):
    """Called on a private copy within one serialized transaction."""
    user = str(user)
    p = state['players'][user]
    settle(state, now)
    require(p['active'] or op in ('profile', 'toggle'), "Bạn đang ngừng tham gia; bật lại trong cài đặt.")
    r = p['realm']
    d = daily(p, now)
    if op == 'profile':
        return "Đã cập nhật hồ sơ."
    if op == 'toggle':
        p['active'] = not p['active']
        return 'Đã bật tu luyện.' if p['active'] else 'Đã ngừng nhận tu vi và hoạt động mới; tác vụ đã nhận vẫn được quyết toán.'
    if op == 'notifications':
        p['notifications'] = not p['notifications']
        return 'Đã bật thông báo riêng qua DM.' if p['notifications'] else 'Đã tắt DM; kết quả vẫn ở hộp thư.'
    if op == 'learn':
        item = args['item']
        require(item in R.RESEARCH, 'Công thức không hợp lệ.')
        require(item not in p['recipes'], 'Bạn đã học công thức này.')
        research = R.RESEARCH[item]
        require(state['sect']['buildings']['library'] >= research['level'], 'Tàng Kinh Các chưa đủ cấp.')
        pay(p, research['coins'])
        p['recipes'].append(item)
        return 'Đã học công thức vĩnh viễn.'
    if op == 'focus':
        require(not p.get('focus_buff'), 'Đã có hiệu ứng chờ trận kế tiếp.')
        p['focus_buff'] = .15 if consume(p, 'focus') else .1
        return 'Đã chuẩn bị Ngưng Thần cho trận kế tiếp.'
    if op == 'strategy':
        require(args['value'] in ('attack', 'balanced', 'careful'), 'Chiến thuật không hợp lệ.')
        p['strategy'] = args['value']
        return 'Đã lưu chiến thuật cho các trận sau.'
    if op == 'potions':
        require(args['value'] in (0, 1, 2), 'Ngân sách tối đa 2 viên.')
        p['potions'] = args['value']
        return f"Đã lưu ngân sách {p['potions']} viên cho mỗi chuyến; chỉ trừ khi xác nhận xuất chiến."
    if op == 'path':
        require(r >= 1 and args['value'] in ('sword', 'body', 'mage'), 'Mở hướng tu luyện ở Trúc Cơ.')
        require(not running(state, user) and not occupied_room(state, user), 'Hãy hoàn tất hoạt động/lobby trước.')
        require(now >= p.get('path_cooldown', 0), 'Đổi hướng đang hồi phục.')
        if p['path_changes'] > 1:
            give(p, 'herb', -5)
            p['path_cooldown'] = now+3600
        p['path_changes'] += 1
        p['path'] = args['value']
        return 'Đã đổi hướng; giữ nguyên tiến trình.'
    if op == 'roll':
        require(not running(state, user) and not occupied_room(state, user) and not p['event'], 'Hoàn tất hoạt động/sự kiện trước khi roll.')
        if p['roll_locked']:
            give(p, 'reroll', -1)
            pay(p, 200*(r+1))
        p['candidate'] = R.stats_roll(rng)
        return 'Đã tạo bộ tư chất mới. Chọn Nhận bộ mới hoặc Giữ bộ cũ.'
    if op == 'accept_roll':
        require(p['candidate'] is not None, 'Chưa có bộ mới.')
        require(not running(state, user) and not occupied_room(state, user) and not p['event'], 'Hoàn tất hoạt động trước khi đổi tư chất.')
        p['genetics'] = p.pop('candidate')
        p['candidate'] = None
        return 'Đã nhận tư chất mới; giữ nguyên tiến trình và trạng thái.'
    if op == 'keep_roll':
        p['candidate'] = None
        return 'Đã giữ bộ tư chất hiện tại.'
    if op == 'craft':
        require(not running(state, user, 'craft'), 'Lò đang luyện.')
        item, count = args['item'], args.get('count', 1)
        require(item not in R.RESEARCH or item in p['recipes'], 'Học công thức bổ sung tại Tàng Kinh Các trước.')
        q = craft_quote(p, item, count)
        q['seconds'] = int(q['seconds']*(1-.02*state['sect']['buildings']['alchemy']))
        for mat, amount in q['materials'].items():
            give(p, mat, -amount)
        pay(p, q['coins'])
        special = item in ('major', 'reroll')
        key = f'{r}:{item}'
        pity = p['craft_pity'].get(key, 0)
        items, good, failed = Counter(), 0, 0
        rate = min(.95, max(.7, .85-.05*r)+min(.05, p['profession_xp']//100*.01)+(.02 if 'Dược Duyên' in p['genetics']['talents'] else 0))
        for _ in range(count):
            success = not special or pity >= 2 or rng.random() < rate
            if success:
                quality = 'fine' if item not in ('minor', 'reroll') and rng.random() < min(.25, .05+p['profession_xp']/10000) else 'normal'
                items[R.item_key(r, item, quality)] += 1
                good += 1
                pity = 0
            else:
                failed += 1
                pity += 1
                for mat, amount in R.RECIPES[item]['materials'].items():
                    items[R.item_key(r, mat)] += amount//2
        result = {'items': dict(items), 'message': f"Luyện {R.NAMES[item]}: {good} thành công, {failed} thất bại. Đã trả thành phẩm/nguyên liệu hoàn vào túi.",
                  'profession_xp': max(1, good*(r+1)*5), 'recipe_key': key, 'pity': pity}
        state['jobs'][action_id] = {'kind': 'craft', 'realm': r, 'users': [user], 'due': now+q['seconds'],
                                   'version': R.VERSION, 'results': {user: result}}
        return f"Đã bắt đầu luyện. Hoàn tất sau {q['seconds']//60} phút, tự trả vào túi kể cả offline."
    if op == 'breakthrough':
        require(r < len(R.XP), 'Bạn đã đến giới hạn nội dung pilot; cảnh giới tiếp theo sẽ được mở sau.')
        require(not running(state, user) and not occupied_room(state, user), 'Hoàn tất hoạt động/lobby trước khi đột phá.')
        require(now >= p['injury_until'], 'Đang trọng thương, chưa thể đột phá.')
        require(p['xp'] >= R.cap(p), 'Tu vi chưa viên mãn.')
        if p['tier'] < 8:
            give(p, 'minor', -R.MINOR_COST[p['tier']])
            p['tier'] += 1
            p['xp'] = 0
            p['roll_locked'] = True
            p['candidate'] = None
            return f"Đột phá thành công: {R.REALMS[r]} tầng {p['tier']+1}."
        fine_major = consume(p, 'major')
        give(p, 'relic', -1)
        pay(p, 80*(r+1))
        boost = .025 if fine_major else 0
        if args.get('guard'):
            fine = consume(p, 'guard')
            boost += .075 if fine else .05
        chance = min(1, [.5, .45, .4, .35][r]+p['insight']*[.15, .125, .1, .1][r]+boost)
        if rng.random() < chance:
            p.update(realm=r+1, tier=0, xp=0, insight=0, candidate=None)
            text = f"Đại đột phá thành công: {R.REALMS[r+1]}!"
            notice(state, 'achievement', user, text, now)
        else:
            p['xp'] -= R.cap(p)*.1
            p['insight'] += 1
            p['injury_start'] = now
            p['injury_until'] = now+[6, 12, 24, 24][r]*3600
            p['injury_shortened'] = False
            text = 'Đột phá thất bại: mất 10% thanh tu vi tầng 9, trọng thương; nhận cảm ngộ cho lần sau.'
        inbox(p, text, now)
        return text
    if op == 'heal_injury':
        require(now < p['injury_until'] and not p['injury_shortened'], 'Không có trọng thương có thể rút ngắn thêm.')
        fine = consume(p, 'injury')
        duration = p['injury_until']-p['injury_start']
        p['injury_until'] = max(now, p['injury_until']-duration*(.5 if fine else .4))
        p['injury_shortened'] = True
        return 'Đã rút 50% thời gian ban đầu.' if fine else 'Đã rút 40% thời gian ban đầu.'
    if op == 'buy':
        item, count = args['item'], args.get('count', 1)
        require(item in R.SHOP and 1 <= count <= 10, 'Cửa hàng chỉ có nguyên liệu phổ thông, 1–10 đơn vị.')
        require(d['shop']+count <= 10, 'Đã đạt giới hạn 10 đơn vị/ngày.')
        pay(p, R.SHOP[item]*count)
        give(p, item, count)
        d['shop'] += count
        return 'Đã mua nguyên liệu.'
    if op == 'gift':
        item, count, target = args['item'], args.get('count', 1), str(args['target'])
        require(target in state['players'] and target != user, 'Người nhận cần có hồ sơ khác bạn trong server.')
        require(item in R.TRADABLE and 1 <= count <= 100, 'Vật phẩm này bị khóa hoặc số lượng không hợp lệ.')
        require(d.get('gift', 0)+count <= 100, 'Tối đa tặng 100 đơn vị/ngày.')
        realm, quality = args.get('realm', r), args.get('quality', 'normal')
        require(isinstance(realm, int) and 0 <= realm < len(R.REALMS), 'Cảnh giới vật phẩm không hợp lệ.')
        require(quality in ('normal', 'fine'), 'Chất lượng không hợp lệ.')
        give(p, item, -count, realm, quality)
        give(state['players'][target], item, count, realm, quality)
        d['gift'] = d.get('gift', 0)+count
        inbox(state['players'][target], f"Nhận {count} {R.NAMES[item]} từ {p['name']}.", now)
        return 'Đã chuyển vật phẩm.'
    if op == 'donate':
        count = args.get('count', 1)
        require(1 <= count <= 20 and d.get('donate', 0)+count <= 20, 'Tối đa hiến 20 Linh thảo/ngày.')
        give(p, 'herb', -count)
        d['donate'] = d.get('donate', 0)+count
        points(state, user, count, now)
        return 'Đã ghi nhận cống hiến và quỹ tông môn.'
    if op == 'vote':
        require(args['building'] in R.BUILDINGS, 'Công trình không hợp lệ.')
        state['sect']['votes'][user] = args['building']
        return 'Đã lưu phiếu ưu tiên nâng cấp.'
    if op == 'garden':
        level = state['sect']['buildings']['garden']
        require(level > 0, 'Dược viên chưa xây dựng.')
        require(not d.get('garden'), 'Đã nhận dược viên hôm nay.')
        give(p, 'herb', min(3, level))
        d['garden'] = True
        return 'Đã nhận Linh thảo từ dược viên.'
    if op == 'library':
        require(state['sect']['buildings']['library'] > 0, 'Tàng Kinh Các chưa xây dựng.')
        require(not d.get('library'), 'Đã nghiên cứu hôm nay.')
        d['library'] = True
        p['profession_xp'] += 5
        return 'Nghiên cứu công thức: +5 kinh nghiệm luyện đan.'
    if op == 'weekly':
        sect = state['sect']
        week = R.week_key(now)
        require(sect['week'] == week and sect['progress'] >= 100, 'Tông môn cần 100 cống hiến trong tuần.')
        require(p['week_points'].get(week, 0) >= 3, 'Cần ít nhất 3 cống hiến tuần này.')
        require(p.get('weekly_claim') != week, 'Đã nhận thưởng tuần.')
        p['weekly_claim'] = week
        p['coins'] += 50*(r+1)
        give(p, 'flower', 2)
        return 'Đã nhận thưởng nhiệm vụ tuần: linh thạch và 2 Linh hoa.'
    if op == 'boss_claim':
        sect = state['sect']
        week = R.week_key(now)
        require(sect['week'] == week and sect['boss_damage'] >= boss_target(state), 'Boss tuần chưa bị hạ.')
        require(user in sect.get('boss_members', []), 'Bạn chưa đóng góp vào boss tuần này.')
        require(user not in sect['boss_claimed'], 'Đã nhận thưởng boss tuần.')
        sect['boss_claimed'].append(user)
        give(p, 'core', 2)
        p['coins'] += 100*(r+1)
        return 'Đã nhận thưởng boss chung: 2 Yêu đan và linh thạch.'
    if op == 'upgrade':
        building = args['building']
        require(building in R.BUILDINGS, 'Công trình không hợp lệ.')
        s = state['sect']
        votes = Counter(s['votes'].values())
        require(votes and votes[building] == max(votes.values()), 'Chọn công trình đang có nhiều phiếu nhất; chủ server quyết định khi hòa.')
        level = s['buildings'][building]
        require(level < 5, 'Công trình đã đạt cấp tối đa pilot.')
        cost = 100*(level+1)
        require(s['fund'] >= cost, f'Cần {cost} điểm xây dựng.')
        s['fund'] -= cost
        s['buildings'][building] += 1
        s['votes'] = {}
        return f"Đã nâng {R.BUILDINGS[building]} lên cấp {level+1}."
    if op == 'dungeon_event':
        job = next((j for j in state['jobs'].values() if j.get('encounter', {}).get('owner') == user and
                    j['encounter'].get('choice') is None and j['encounter']['opens'] <= now < j['encounter']['expires']), None)
        require(job is not None, 'Không có điểm lựa chọn phó bản đang mở cho bạn.')
        event = job['encounter']
        choice = args['choice']
        require(choice in ('inspect', 'open', 'leave'), 'Lựa chọn không hợp lệ.')
        event['choice'] = choice
        if choice == 'leave':
            return 'Đội bỏ qua an toàn và tiếp tục.'
        erng = random.Random(event['seed']+(1 if choice == 'inspect' else 2))
        good = erng.random() < (.7 if choice == 'inspect' else .5)
        for uid, result in job['results'].items():
            if not result.get('points'):
                continue
            # Only newly earned expedition money is at risk, never private bags or XP.
            change = (10 if choice == 'inspect' else 20)*(job['realm']+1)
            result['coins'] = max(result.get('checkpoint_coins', 0), result['coins']+(change if good else -change))
            result['message'] += '\nKỳ ngộ: thêm linh thạch.' if good else '\nKiếp nạn: giảm linh thạch chặng boss, giữ thưởng chặng đầu.'
        return 'Đã giải quyết dấu tích; đội tiếp tục, không cần thao tác thêm.'
    if op == 'event':
        e = p['event']
        require(e is not None and now < e['expires'], 'Sự kiện đã kết thúc.')
        choice = args['choice']
        require(choice in ('inspect', 'open', 'leave'), 'Lựa chọn không hợp lệ.')
        p['event'] = None
        if choice == 'leave':
            return 'Bạn rời đi an toàn, không thưởng và không phạt.'
        erng = random.Random(e['seed']+(1 if choice == 'inspect' else 2))
        chance = max(.2, min(.85, .55+e['fortune']/500-e['calamity']/700+(.1 if choice == 'inspect' else 0)))
        if erng.random() < chance:
            reward = 20 if choice == 'inspect' else 50
            p['coins'] += reward*(e['realm']+1)
            give(p, 'flower', 1 if choice == 'inspect' else 2, e['realm'])
            return 'Cơ duyên: tìm thấy linh thạch và Linh hoa. Đã cất vào túi.'
        # Hidden ordinary calamity never takes XP, gear or realm progress.
        loss = min(bag(p, 'herb', e['realm']), 1 if choice == 'inspect' else 2)
        give(p, 'herb', -loss, e['realm'])
        return f"Gặp trận pháp cũ; mất {loss} Linh thảo để hóa giải. Không mất tu vi hoặc trang bị."
    if op == 'explore':
        require(not running(state, user, 'explore'), 'Đang có chuyến thám hiểm.')
        require(d.get('explore', 0) < 3, 'Hết 3 lượt thám hiểm có thưởng hôm nay.')
        area = args.get('area', 'herb')
        require(area in ('herb', 'water', 'marrow'), 'Địa điểm không hợp lệ.')
        d['explore'] = d.get('explore', 0)+1
        items = {R.item_key(r, area): rng.randint(3, 5) if area != 'marrow' else 1}
        event = None
        event_rate = max(.1, min(.35, .2+(p['genetics']['fortune']+p['genetics']['calamity']-100)/1000))
        if rng.random() < event_rate and p['event'] is None:
            event = {'seed': rng.getrandbits(64), 'fortune': p['genetics']['fortune'],
                     'calamity': p['genetics']['calamity'], 'realm': r, 'expires': now+86400}
        result = {'coins': 25*(r+1), 'xp': 20, 'items': items, 'points': 2, 'event': event,
                  'message': f"Thám hiểm hoàn tất: nhận {R.NAMES[area]}, linh thạch và tu vi."}
        state['jobs'][action_id] = {'kind': 'explore', 'realm': r, 'users': [user], 'due': now+1200,
                                   'version': R.VERSION, 'results': {user: result}}
        return 'Đã lên đường; 20 phút sau tự nhận phần thưởng.'
    if op in ('hunt', 'dungeon', 'sect_boss'):
        require(not occupied_room(state, user), 'Rời đội đang chờ trước khi đánh cá nhân.')
        return start_battle(state, [user], op, now, rng, action_id)
    if op == 'room_create':
        existing = next((rid for rid, room in state['rooms'].items() if room['owner'] == user), None)
        if existing:
            return existing
        require(not occupied_room(state, user) and not running(state, user, 'combat'), 'Bạn đang trong đội hoặc trận khác.')
        state['rooms'][action_id] = {'owner': user, 'members': [user], 'ready': {}, 'message_id': None, 'expires': now+1800}
        return action_id
    if op in ('room_join', 'room_ready', 'room_leave', 'room_start'):
        room = state['rooms'].get(args['room'])
        require(room is not None, 'Đội đã hết hạn hoặc xuất phát.')
        if op == 'room_join':
            require(not occupied_room(state, user) and not running(state, user, 'combat'), 'Bạn đã ở trong đội/trận khác.')
            require(len(room['members']) < 4, 'Đội đã đủ 4 người.')
            require(p['realm'] == state['players'][room['owner']]['realm'], 'Pilot yêu cầu cùng đại cảnh giới.')
            room['members'].append(user)
            room['ready'] = {}
            return 'Đã vào đội. Các thành viên xác nhận sẵn sàng.'
        require(user in room['members'], 'Bạn chưa ở trong đội này.')
        if op == 'room_leave':
            room['members'].remove(user)
            room['ready'] = {}
            if not room['members']:
                del state['rooms'][args['room']]
            else:
                room['owner'] = room['members'][0]
            return 'Đã rời đội.'
        if op == 'room_ready':
            room['ready'][user] = {'strategy': p['strategy'], 'potions': p['potions']}
            return f"Sẵn sàng: {p['strategy']}, tối đa {p['potions']} đan."
        require(user == room['owner'], 'Chỉ chủ đội được xuất phát.')
        require(2 <= len(room['members']) <= 4 and all(u in room['ready'] for u in room['members']), 'Cần 2–4 người và tất cả sẵn sàng.')
        result = start_battle(state, room['members'], 'dungeon', now, rng, action_id, room['ready'])
        del state['rooms'][args['room']]
        return result
    raise GameError('Thao tác chưa được hỗ trợ.')


def start_battle(state, users, kind, now, rng, action_id, ready=None):
    combatants, eligible = [], {}
    realm = state['players'][users[0]]['realm']
    for user in users:
        p = state['players'][user]
        require(p['active'] and not running(state, user, 'combat'), 'Có thành viên đang trong trận khác hoặc ngừng tham gia.')
        snapshot = copy.deepcopy(p)
        if ready:
            snapshot.update(ready[user])
        count = snapshot['potions']
        require(bag(p, 'heal')+bag(p, 'heal', quality='fine') >= count, f"{p['name']} chưa đủ {count} Hồi Xuân Đan; giảm ngân sách hoặc luyện thêm.")
        snapshot['_fine_potions'] = consume(p, 'heal', count)
        snapshot['_potions'] = count
        snapshot['_injured'] = now < p['injury_until']
        snapshot['_focus'] = p.pop('focus_buff', 0)
        if kind == 'sect_boss':
            boss_target(state)
        snapshot['_shield'] = .02*state['sect']['buildings']['shield']
        combatants.append((user, snapshot))
        d = daily(p, now)
        quota_key = kind
        if kind == 'sect_boss':
            quota_key = 'sect_boss:'+R.week_key(now)
            used = p.get(quota_key, 0)
        else:
            used = d.get(quota_key, 0)
        eligible[user] = used < R.LIMITS[kind]
    first = battle(combatants, realm, 'hunt' if kind in ('hunt', 'dungeon') else 'boss', rng.getrandbits(64))
    final = first
    if kind == 'dungeon' and first['won']:
        next_party = []
        for uid, snap in combatants:
            clone = copy.deepcopy(snap)
            used = first['participants'][uid]['used']
            clone['_potions'] -= used
            clone['_fine_potions'] = min(clone['_fine_potions'], clone['_potions'])
            clone['_health'] = first['participants'][uid]['health']
            clone['_mana'] = first['participants'][uid]['mana']
            next_party.append((uid, clone))
        final = battle(next_party, realm, 'boss', rng.getrandbits(64))
        for uid, part in final['participants'].items():
            part['used'] += first['participants'][uid]['used']
    results = {}
    duration = first['seconds']+(final['seconds']+30 if final is not first else 0)
    for user, snap in combatants:
        p = state['players'][user]
        items = Counter()
        used = final['participants'][user]['used']
        unused = snap['_potions']-used
        unused_fine = min(snap['_fine_potions'], unused)
        items[R.item_key(realm, 'heal')] += unused-unused_fine
        items[R.item_key(realm, 'heal', 'fine')] += unused_fine
        coins, earned, count = 0, 0, 0
        if (first['won'] or kind == 'sect_boss') and eligible[user]:
            count = 3 if kind == 'hunt' else 8
            coins, earned = (12*(realm+1), 15) if kind == 'hunt' else (55*(realm+1), 70)
            if kind == 'hunt':
                items[R.item_key(realm, 'blood')] += 1
            elif kind == 'dungeon' and final['won']:
                items[R.item_key(realm, 'core')] += 1
                items[R.item_key(realm, 'fragment')] += 1
                if rng.random() < .15:
                    items[R.item_key(realm, 'relic')] += 1
            elif kind == 'dungeon':
                coins, earned, count = 12*(realm+1), 15, 3
                items[R.item_key(realm, 'blood')] += 1
            else:
                items[R.item_key(realm, 'herb')] += 5
            if kind == 'sect_boss':
                key = 'sect_boss:'+R.week_key(now)
                p[key] = p.get(key, 0)+1
            else:
                d = daily(p, now)
                d[kind] = d.get(kind, 0)+1
        text = ('Chiến thắng' if final['won'] else 'Thất bại')+f" · {kind}. "
        text += f"Dùng {final['participants'][user]['used']} đan; thưởng {coins} linh thạch, {earned} tu vi. "
        if not eligible[user]:
            text += 'Lượt hỗ trợ, không nhận thưởng. '
        text += ('Đã giữ thưởng chặng đầu. ' if kind == 'dungeon' and first['won'] and not final['won'] else '')
        text += '\n'.join(final['log'])
        results[user] = {'items': dict(items), 'coins': coins, 'xp': earned, 'points': count, 'message': text,
                         'checkpoint_coins': 12*(realm+1) if kind == 'dungeon' and first['won'] and eligible[user] else 0,
                         'boss_damage': round(final['participants'][user].get('damage', 0)/(2**realm)) if kind == 'sect_boss' and eligible[user] else 0}
    state['jobs'][action_id] = {'kind': 'combat', 'realm': realm, 'users': list(users),
                               'due': now+duration, 'results': results, 'version': R.VERSION,
                               'combat': final, 'first_stage': first if kind == 'dungeon' else None}
    if kind == 'dungeon' and first['won']:
        state['jobs'][action_id]['encounter'] = {
            'owner': users[0], 'opens': now+first['seconds'], 'expires': now+first['seconds']+60,
            'seed': rng.getrandbits(64), 'choice': None}
        state['jobs'][action_id]['due'] += 60
        duration += 60
    return f"Đã xuất chiến auto. Kết quả sau khoảng {duration} giây, kể cả khi bạn offline."
