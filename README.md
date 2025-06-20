# Virtus Bot

Một Discord bot để quản lý điểm kinh nghiệm người dùng (user experience points).

## Tính năng

- Quản lý điểm kinh nghiệm người dùng
- Tích hợp với Supabase database
- Hệ thống sự kiện và tác vụ tự động

## Yêu cầu hệ thống

- Python 3.9+
- uv package manager
- Discord Bot Token
- Supabase credentials

## Cài đặt và chạy với Docker

### 1. Clone repository
```bash
git clone <repository-url>
cd virtus-bot
```

### 2. Tạo file .env
Tạo file `.env` với các biến môi trường cần thiết:
```env
BOT_TOKEN=your_discord_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=your_database_url
```

### 3. Build và chạy với Docker Compose
```bash
# Build image
docker-compose build

# Chạy bot
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng bot
docker-compose down
```

### 4. Chạy với Docker trực tiếp
```bash
# Build image
docker build -t virtus-bot .

# Chạy container
docker run -d \
  --name virtus-bot \
  --env-file .env \
  --restart unless-stopped \
  virtus-bot
```

## Phát triển local

### 1. Cài đặt dependencies
```bash
# Cài đặt uv
pip install uv

# Sync dependencies
uv sync
```

### 2. Chạy bot
```bash
uv run python main.py
```

## Cấu trúc dự án

```
virtus-bot/
├── apps/           # Các ứng dụng Discord commands
├── core/           # Core bot functionality
├── models/         # Database models
├── repositories/   # Data access layer
├── utils/          # Utility functions
├── infra/          # Infrastructure code
├── main.py         # Entry point
├── pyproject.toml  # Project configuration
└── uv.lock         # Locked dependencies
```

## Dependencies

- discord.py >= 2.3.2
- python-dotenv >= 1.0.0
- sqlalchemy >= 2.0.0
- supabase >= 2.3.0
- asyncpg >= 0.29.0

## License

Xem file [LICENSE](LICENSE) để biết thêm chi tiết.