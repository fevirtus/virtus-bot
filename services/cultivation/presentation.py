"""Player-facing Vietnamese copy, shared by Discord and durable results."""
from . import rules as R

STRATEGIES = {'balanced': 'Cân bằng', 'attack': 'Tấn công', 'careful': 'Thận trọng'}
ACTIVITIES = {'explore': 'Thám hiểm', 'hunt': 'Săn quái', 'dungeon': 'Phó bản',
              'sect_boss': 'Boss tông môn', 'combat': 'Chiến đấu', 'craft': 'Luyện đan'}
STATS = {'hp': 'Sinh lực', 'attack': 'Công kích', 'defense': 'Phòng ngự', 'mana': 'Linh lực'}
TALENTS = {
    'Kiếm Tâm': 'Tỉ lệ chí mạng 17% thay vì 12%.',
    'Dược Duyên': 'Tăng 2 điểm % tỉ lệ luyện đan đại đột phá và Tẩy Tủy Đan (tối đa 95%).',
    'Phúc Tinh': 'Cộng 10 điểm Cơ duyên lúc tạo tư chất, tối đa 100; đã tính vào số hiển thị.',
    'Kiên Cường': 'Tăng 4% sinh lực tối đa khi chiến đấu.',
    'Linh Hải': 'Tăng 10% linh lực khi chiến đấu.',
    'Nghịch Thiên': 'Tăng 4% sát thương khi sinh lực dưới 30%.',
}
ROOT_HELP = 'Ngũ hành khắc chế: Kim → Mộc → Thổ → Thủy → Hỏa → Kim. Khắc đối thủ: +5% công kích; bị khắc: −5%.'
GUIDE = (
    '**Bắt đầu tu tiên**\n'
    '1. Chat hoặc voice cùng bạn bè để nhận **tu vi** (kinh nghiệm). Thanh tu vi đầy thì cần đột phá, không tự lên tầng.\n'
    '2. **Thám hiểm** 20 phút để kiếm Linh thảo/Linh tuyền; **Săn quái** kiếm Yêu huyết. Hoạt động tự chạy, không cần bấm từng lượt.\n'
    '3. Luyện **Tụ Khí Đan** bằng 2 Linh thảo + 1 Linh tuyền + 8 linh thạch ở Luyện Khí. Chờ đan hoàn tất rồi chọn **Đột phá**.\n'
    '4. Tầng 9 lên đại cảnh giới cần đan đại đột phá, linh vật từ boss và linh thạch; có thể thất bại.\n\n'
    '**Xem tiến trình và kết quả ở đâu?**\n'
    'Mỗi người có một bảng hoạt động tại kênh tu tiên, tự cập nhật khoảng 30 giây/lần. Kết quả ghi rõ vật phẩm và tu vi thực nhận, đồng thời lưu trong **Hộp thư**. '
    'Bảng cá nhân là ảnh chụp tại lúc mở: bấm **Cập nhật** để lấy trạng thái mới. DM là tùy chọn, mặc định tắt.\n\n'
    '**Chiến thuật**\nCân bằng: chỉ số gốc. Tấn công: +15% công kích, chịu thêm 15% sát thương. Thận trọng: −10% công kích, giảm 20% sát thương nhận.\n'
    'Hồi Xuân Đan tự dùng dưới 30% sinh lực, phần chưa dùng trả lại túi. Phó bản gồm quái đầu đường và boss; chủ đội có thể chọn dấu tích giữa đường, bỏ qua vẫn tiếp tục.\n'
    'Lượt thưởng: thám hiểm 3/ngày, săn quái 5/ngày, phó bản 2/ngày, boss tông môn 2/tuần. Ngoài lượt thưởng, chiến đấu chỉ hỗ trợ và vẫn có thể tốn đan.'
)


def genetics_text(g, previous=None):
    lines = [f"**Linh căn {g['root']}** — thuộc tính ngũ hành dùng khi chiến đấu."]
    for talent in g['talents']:
        lines.append(f"• **{talent}**: {TALENTS.get(talent, 'Chưa có mô tả.')}")
    lines.append('**Chỉ số nền** (100 = chuẩn, 110 = +10%; chưa tính cảnh giới/thiên phú):')
    stats = []
    for key, label in STATS.items():
        value = g['stats'][key]
        delta = f" ({value-previous['stats'][key]:+d})" if previous else ''
        stats.append(f'{label} {value}{delta}')
    lines.append(' · '.join(stats))
    lines.append(f"Cơ duyên **{g['fortune']}/100** · Kiếp số **{g['calamity']}/100**")
    if previous:
        lines.append(f"So với hiện tại: Cơ duyên {g['fortune']-previous['fortune']:+d} · Kiếp số {g['calamity']-previous['calamity']:+d}.")
    return '\n'.join(lines)


def aptitude_text(p):
    text = '**Tư chất là gì?**\nBộ đặc điểm gồm linh căn, hai thiên phú, bốn chỉ số nền, Cơ duyên và Kiếp số. Không có một điểm tổng để xếp bộ nào luôn tốt hơn.\n\n'
    text += '**Bộ đang sử dụng**\n'+genetics_text(p['genetics'])
    if p.get('candidate'):
        text += '\n\n**Bộ mới — CHƯA áp dụng**\n'+genetics_text(p['candidate'], p['genetics'])
        text += '\nChọn **Nhận bộ mới** để thay toàn bộ, hoặc **Giữ bộ cũ** để bỏ bộ vừa tạo.'
    text += '\n\n**Thiên phú** là hai hiệu ứng bị động nêu trên.\n'+ROOT_HELP
    text += '\n**Cơ duyên** cao tăng cơ hội kết quả tốt khi chọn dấu tích. **Kiếp số** cao giảm cơ hội đó. Cả hai cùng ảnh hưởng tần suất gặp dấu tích; Kiếp số cao không phải lợi thế thuần túy.'
    text += '\nTạo lại miễn phí vô hạn trước lần đột phá tầng đầu tiên; sau đó cần Tẩy Tủy Đan và linh thạch.'
    return text


def job_name(job):
    name = ACTIVITIES.get(job.get('activity', job['kind']), 'Hoạt động')
    if job.get('item'):
        name += ' · '+R.NAMES[job['item']]
    if job.get('area'):
        name += ' · tìm '+R.NAMES[job['area']]
    if len(job['users']) > 1:
        name += f" · đội {len(job['users'])} người"
    return name


def progress_lines(state, uid, now):
    lines = []
    for job in state['jobs'].values():
        if str(uid) not in job['users']:
            continue
        status = 'Đang thực hiện'
        event = job.get('encounter')
        if event:
            if now < event['opens']:
                status = 'Chặng 1: vượt quái đầu đường'
            elif now < event['expires']:
                status = 'Nghỉ giữa chặng; chủ đội có thể chọn dấu tích' if not event['choice'] else 'Đã chọn dấu tích; chuẩn bị gặp boss'
            else:
                status = 'Chặng 2: đối đầu boss'
        lines.append(f"**{job_name(job)}** — {status}.\nDự kiến xong <t:{int(job['due'])}:R> (<t:{int(job['due'])}:t>); tự trả thưởng, không cần bấm nhận.")
    return lines


def result_text(job, result, actual_xp):
    message = result['message']
    if job['kind'] == 'combat' and 'activity' not in job:
        message = '**Chiến đấu đã hoàn tất** (chuyến bắt đầu trước bản cập nhật giao diện).'
    lines = [message]
    if 'coins' in result:
        lines.append(f"Linh thạch: **+{result['coins']}** · Tu vi thực nhận: **+{actual_xp:g}**")
    if result.get('xp', 0) > actual_xp:
        lines.append('Tu vi nhận ít hơn mức gốc do đã đầy thanh tu vi, trọng thương hoặc đổi cảnh giới. Đầy tu vi: hãy chuẩn bị đột phá.')
    items = []
    for key, count in result.get('items', {}).items():
        if count <= 0:
            continue
        realm, item, quality = key.split(':')
        suffix = ' (đan chưa dùng, trả lại)' if job['kind'] == 'combat' and item == 'heal' else ''
        items.append(f"{R.NAMES.get(item, item)} ×{count} · {R.REALMS[int(realm)]} · {'Thượng phẩm' if quality == 'fine' else 'Đạt chuẩn'}{suffix}")
    lines.append('**Đã vào túi:**\n'+'\n'.join('• '+i for i in items) if items else 'Không có vật phẩm nhận thêm.')
    if result.get('points'):
        lines.append(f"Cống hiến: +{result['points']}")
    if result.get('boss_damage'):
        lines.append(f"Sát thương đóng góp boss tuần: {result['boss_damage']}")
    return '\n'.join(lines)
