# Virtus Bot

Một Discord bot mã nguồn mở tích hợp Admin Dashboard để quản lý cấu hình và điểm kinh nghiệm người dùng.

## Tính năng

-   **Admin Dashboard (Web UI)**: Quản lý cấu hình bot trực quan.
-   **Dynamic Configuration**: Thay đổi cấu hình (Channel ID, Admin ID) mà không cần restart.
-   **Modules (Cogs)**:
    -   `HomeDebt`: Quản lý chi tiêu chung.
    -   `GroupDebt`: Chia tiền nhóm bạn và cộng dồn nợ theo kênh.
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

## Chia tiền nhóm bạn (Group Debt)

Module riêng với `HomeDebt` (tiền nhà); mỗi kênh hoặc thread có một sổ nợ riêng.

1. Trong Admin Dashboard, chọn server và bật **Group Debt**.
   `CHANNEL_GROUP_DEBT_IDS` là danh sách ID kênh được phép, cách nhau bằng dấu phẩy.
   Để trống để cho phép mọi kênh. Thread dùng ID của chính thread đó.
2. Sau buổi chơi, người ứng tiền dùng `/chia tien:600k`, chọn **tất cả người tham gia
   buổi này** ở danh sách, rồi bấm **Xác nhận chia tiền**. Bot tự đếm người và chia đều;
   chọn cả bạn nếu bạn cũng tham gia. Có thể thêm `ghichu`. Mỗi lần chọn lại danh sách,
   tối đa 25 người, không cần thiết lập nhóm hoặc nhập số người. Nợ cũ vẫn được giữ.
   Form có hiệu lực 5 phút; hết hạn thì dùng lại lệnh. Chưa xác nhận thì chưa ghi nợ.
3. Dùng `/no` để xem số dư và gợi ý ai chuyển cho ai. Đây là nợ **ròng trong nhóm**,
   tự bù trừ giữa các lần ứng tiền, không phải nợ cố định giữa từng cặp người.
4. Sau khi chuyển thật, người trả dùng `/tra nguoi:@An tien:200k` để giảm nợ ngay,
   không cần người nhận duyệt. Được trả từng phần; bot từ chối trả vượt số nợ ròng
   của người trả hoặc số được nhận của người nhận. Lệnh chỉ ghi sổ, không chuyển tiền.
5. Nhập nhầm thì bấm **Hoàn tác** trên tin nhắn kết quả, hoặc dùng `/lichsu` lấy mã rồi
   `/hoantac ma:<mã>`. Bạn chỉ hoàn tác được khoản mình tạo; quản trị viên có thể hỗ trợ.
   Lịch sử giữ khoản đã hoàn tác. Hoàn tác đảo tác động của khoản đó trên số dư hiện tại,
   kể cả khi đã có giao dịch mới. Nút hoàn tác dùng được sau khi bot restart.

Tiền nhập bằng đồng (`600000`) hoặc hậu tố `k` (`600k`, `150.5k`);
không dùng dấu phân cách hàng nghìn trong số nhập. Bot hiển thị `600.000 ₫`.
Phần dư khi chia tiền lẻ được phân bổ theo thứ tự Discord user ID để tổng luôn khớp.
`/lichsu trang:2` xem 10 giao dịch tiếp theo; `/no trang:2` xem tiếp nếu có nhiều thành viên cũ.

Ví dụ ba người: bạn ứng 600k → bạn được nhận 400k, An và Bình cần trả 200k/người.
Hôm sau An ứng 300k → bạn được nhận 300k, An hết nợ, Bình cần trả 300k.
Bình trả bạn 200k → bạn còn được nhận 100k, Bình còn cần trả 100k.

Các bảng `group_debt_*` được tạo tự động khi khởi động bằng cơ chế hiện có.
Không cần thay đổi cấu trúc bảng `home_debt` hoặc chuyển số nợ tiền nhà sang sổ nhóm.

### Kiểm thử

```bash
uv run --frozen --with 'aiosqlite>=0.20.0,<1' python -m unittest discover -s tests -v
```

Hoặc cài thư viện dự án và `pip install -r requirements-test.txt` trong môi trường Python riêng.
Mặc định kiểm thử sổ nợ bằng SQLite tạm trong bộ nhớ. Để kiểm thử thêm khóa hàng
và các thao tác đồng thời, đặt `GROUP_DEBT_TEST_POSTGRES_URL` tới **database kiểm thử**
theo dạng `postgresql+asyncpg://...`. Mỗi test tạo schema tạm riêng rồi xóa schema đó.
GitHub Actions chạy bộ kiểm thử này với PostgreSQL 15, trước khi build/publish image.

## Docker Support

Dự án hỗ trợ triển khai nhanh bằng Docker Compose với image đã được build sẵn.

### Yêu cầu
- Docker
- Docker Compose

### Cài đặt và chạy
1.  Tạo file `.env` (nếu chưa có):
    ```bash
    cp .env.example .env
    # Hoặc tạo mới và điền các giá trị cần thiết
    ```
    > **Lưu ý Database**:
    > - Mặc định, bot sẽ kết nối tới Postgres container được tạo kèm trong `docker-compose.yml`.
    > - Nếu bạn muốn dùng Database riêng (bên ngoài Docker hoặc host khác), hãy cấu hình biến `POSTGRES_URL` trong file `.env`.
    > - Nếu dùng Database mặc định, bạn không cần sửa `POSTGRES_URL`.

2.  Chạy ứng dụng:
    ```bash
    docker-compose up -d
    ```

3.  Cập nhật phiên bản mới nhất:
    ```bash
    docker-compose pull
    docker-compose up -d
    ```

4.  Truy cập Admin Dashboard tại `http://localhost:8000`.

### Cấu hình Docker Compose
File `docker-compose.yml` bao gồm:
-   `bot`: Sử dụng image `ghcr.io/fevirtus/virtus-bot:latest` (ghi đè bằng `VIRTUS_IMAGE` nếu cần).
-   `db`: PostgreSQL 15 (chạy song song phục vụ cho bot).
    -   Dữ liệu được lưu tại volume `postgres_data`.
