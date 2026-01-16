# Virtus Bot

Một Discord bot mã nguồn mở tích hợp Admin Dashboard để quản lý cấu hình và điểm kinh nghiệm người dùng.

## Tính năng

-   **Admin Dashboard (Web UI)**: Quản lý cấu hình bot trực quan.
-   **Dynamic Configuration**: Thay đổi cấu hình (Channel ID, Admin ID) mà không cần restart.
-   **Modules (Cogs)**:
    -   `HomeDebt`: Quản lý chi tiêu chung.
    -   `NoiTu`: Trò chơi nối từ.
    -   `Score`: Hệ thống điểm kinh nghiệm.
-   **Tech Stack**: Python, Discord.py, FastAPI, SQLAlchemy (Async), PostgreSQL.

## Yêu cầu hệ thống

-   Python 3.9+
-   uv package manager (khuyến nghị) hoặc pip
-   Discord Bot Token
-   PostgreSQL Database

## Cài đặt và chạy

### 1. Clone repository
```bash
git clone <repository-url>
cd virtus-bot
```

### 2. Cài đặt dependencies
Dự án sử dụng `uv` để quản lý package.
```bash
pip install uv
uv sync
```

### 3. Cấu hình môi trường
Tạo file `.env` từ `CONFIG_EXAMPLE.md` (hoặc tạo mới):
```env
BOT_TOKEN=your_discord_bot_token
POSTGRES_URL=postgresql+asyncpg://user:password@host:5432/dbname
```
> **Auto-Seed**: Khi khởi động, Bot sẽ tự động sao chép `CHANNEL_HOME_DEBT_ID`, `CHANNEL_NOI_TU_IDS`, `ADMIN_IDS` từ `.env` vào Database nếu chưa có.
> Bạn có thể quản lý chúng qua Admin UI sau đó.

### 4. Chạy Bot & Web Server
```bash
uv run python main.py
```
-   **Bot**: Sẽ tự động đăng nhập và online.
-   **Admin Dashboard**: Truy cập tại `http://localhost:8000`.

## Sử dụng Admin Dashboard

1.  Truy cập `http://localhost:8000`.
2.  Thêm các cấu hình cần thiết:
    -   `CHANNEL_HOME_DEBT_ID`: ID của kênh channel chat chi tiêu.
    -   `CHANNEL_NOI_TU_IDS`: Danh sách ID các kênh chơi nối từ (cách nhau bởi dấu phẩy).
    -   `ADMIN_IDS`: Danh sách ID của admin bot (cách nhau bởi dấu phẩy).

## Cấu trúc dự án

```
virtus-bot/
├── bot/                # Mã nguồn Bot
│   ├── cogs/           # Các chức năng (Modules)
│   └── core/           # Core bot class
├── web/                # Mã nguồn Web Admin
│   ├── static/         # Frontend assets (HTML/CSS/JS)
│   └── server.py       # FastAPI application
├── models/             # Database models
├── repositories/       # Data access layer
├── infra/              # Infrastructure (DB connection)
├── main.py             # Entry point (Runs Bot + Web)
└── ...
```

## Docker Support
Dự án hỗ trợ chạy bằng Docker.
```bash
docker-compose up --build -d
```