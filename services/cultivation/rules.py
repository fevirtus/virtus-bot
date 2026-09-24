"""Versioned pilot rules. Values remain separate from Discord and storage."""
from datetime import datetime, timedelta, timezone

VERSION = "1.0.0"
REALMS = ["Luyện Khí", "Trúc Cơ", "Kim Đan", "Nguyên Anh", "Hóa Thần"]
XP = [
    [72, 99, 135, 180, 216, 270, 324, 396, 675],
    [200, 275, 375, 500, 600, 750, 900, 1100, 1875],
    [480, 660, 900, 1200, 1440, 1800, 2160, 2640, 4500],
    [960, 1320, 1800, 2400, 2880, 3600, 4320, 5280, 9000],
]
MINOR_COST = [1, 1, 1, 2, 2, 2, 3, 3]
NAMES = {
    "herb": "Linh thảo", "water": "Linh tuyền", "blood": "Yêu huyết",
    "core": "Yêu đan", "flower": "Linh hoa", "marrow": "Tẩy tủy thảo",
    "fragment": "Mảnh linh vật", "relic": "Linh vật đột phá",
    "minor": "Tụ Khí Đan", "major": "Đan đại đột phá", "heal": "Hồi Xuân Đan",
    "injury": "Dưỡng Thương Đan", "guard": "Hộ Mạch Đan", "reroll": "Tẩy Tủy Đan",
}
RECIPES = {
    "minor": {"materials": {"herb": 2, "water": 1}, "coins": 8, "seconds": 60},
    "heal": {"materials": {"herb": 1, "blood": 1}, "coins": 5, "seconds": 60},
    "injury": {"materials": {"herb": 3, "water": 2}, "coins": 15, "seconds": 180},
    "guard": {"materials": {"flower": 2, "water": 2}, "coins": 25, "seconds": 300},
    "major": {"materials": {"herb": 8, "water": 4, "core": 2}, "coins": 50, "seconds": 600},
    "reroll": {"materials": {"marrow": 2, "herb": 5, "water": 3}, "coins": 80, "seconds": 600},
}
TRADABLE = {"herb", "water", "blood", "flower", "heal", "minor", "injury"}
SHOP = {"herb": 4, "water": 5}
LIMITS = {"explore": 3, "hunt": 5, "dungeon": 2, "sect_boss": 2}
ROOTS = ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]
TALENTS = ["Kiếm Tâm", "Dược Duyên", "Phúc Tinh", "Kiên Cường", "Linh Hải", "Nghịch Thiên"]
BUILDINGS = {"alchemy": "Đan phòng", "garden": "Dược viên", "library": "Tàng Kinh Các", "shield": "Hộ Sơn Đại Trận"}


def day_key(now):
    return str(int((now + 3 * 3600) // 86400))


def week_key(now):
    shifted = datetime.fromtimestamp(now, timezone.utc) + timedelta(hours=3)
    return (shifted.date() - timedelta(days=shifted.weekday())).isoformat()


def item_key(realm, item, quality="normal"):
    return f"{realm}:{item}:{quality}"


def stats_roll(rng):
    attack, defense = rng.randint(-10, 10), rng.randint(-10, 10)
    talents = rng.sample(TALENTS, 2)
    return {"root": rng.choice(ROOTS), "talents": talents,
            "stats": {"hp": 100-attack, "attack": 100+attack, "defense": 100+defense, "mana": 100-defense},
            "fortune": min(100, rng.randint(1, 100)+(10 if "Phúc Tinh" in talents else 0)), "calamity": rng.randint(1, 100)}


def realm_name(player):
    return REALMS[player['realm']]


def cap(player):
    return XP[player['realm']][player['tier']] if player['realm'] < len(XP) else 0

# Optional research recipes never gate a required breakthrough.
NAMES['focus'] = 'Ngưng Thần Đan'
RECIPES['focus'] = {'materials': {'flower': 1, 'water': 2}, 'coins': 15, 'seconds': 180}
RESEARCH = {'focus': {'level': 1, 'coins': 50}}
ITEM_INFO = {
    'herb': ('Luyện đan, hiến tông môn', 'Thám hiểm / sinh hoạt / cửa hàng'),
    'water': ('Dung môi luyện đan', 'Thám hiểm / sinh hoạt / cửa hàng'),
    'blood': ('Luyện đan hồi phục', 'Săn quái / chặng đầu phó bản'),
    'core': ('Luyện đan đại đột phá', 'Boss phó bản / boss tuần'),
    'flower': ('Luyện đan hỗ trợ', 'Kỳ ngộ / nhiệm vụ tuần'),
    'marrow': ('Luyện Tẩy Tủy Đan', 'Thám hiểm'),
    'fragment': ('Tự ghép 5 mảnh thành linh vật', 'Boss phó bản'),
    'relic': ('Đột phá đại cảnh giới', 'Boss / ghép mảnh'),
    'minor': ('Đột phá tầng nhỏ', 'Luyện đan'),
    'major': ('Đột phá đại cảnh giới', 'Luyện đan'),
    'heal': ('Tự hồi HP khi chiến đấu', 'Luyện đan'),
    'injury': ('Rút thời gian trọng thương một lần', 'Luyện đan'),
    'guard': ('Tăng xác suất đại đột phá', 'Luyện đan'),
    'reroll': ('Roll lại tư chất sau tầng đầu', 'Luyện đan'),
    'focus': ('Tăng 10% mana cho trận kế tiếp', 'Nghiên cứu ở Tàng Kinh Các rồi luyện'),
}
