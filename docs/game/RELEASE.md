# Phát hành tu tiên 1.0 — 2026-09-24

Trạng thái: đã triển khai thành công và kiểm chứng trực tiếp trên cụm ngày 2026-09-24.

- Hoàn tất các hạng mục thiếu của pilot; chi tiết ở IMPLEMENTATION.md và D032.
- 35 kiểm thử runtime/Discord adapter/PostgreSQL/HTTP đạt, 9 kiểm thử mô hình lịch sử đạt; Python compile và kiểm tra whitespace đạt.
- Mô phỏng 100 nhân vật bằng runtime thực: Trúc Cơ trung bình 10,83 ngày, Kim Đan 32,62, Nguyên Anh 81,08, Hóa Thần 179,24. Seed, giả định và P10/P90 nằm trong `balance/runtime-results.json` và `scripts/simulate_runtime.py`.
- Backup nhất quán chỉ đọc qua pod đang chạy đã hoàn tất; không đưa backup hoặc secret vào Git/image. 7 bảng, 46.487 bản ghi cũ. Phục hồi vào PostgreSQL local và chạy startup migration hai lần, so sánh toàn bộ bản ghi: không thay đổi dữ liệu cũ.
- Production: namespace `virtus-bot`, deployment `virtus-bot`, container `bot`, replicas=1, strategy=Recreate. Dùng lại secret `virtus-bot-env` và database hiện tại, không tạo/reset database.
- Image trước phát hành: `fevirtus/virtus-bot@sha256:d67b288607ff1ef30cb5e72ad6ef7a4fc8ddaea42dd27d668c2e8d23de107bce`.
- CI mới chạy test với PostgreSQL trước publish; tag immutable `sha-<commit>`. Pull request không đăng nhập registry hoặc push image.

## Kết quả triển khai

- Commit source: `13da7c780ac1042c36d8eefca1d55ec9369c5628`.
- Image đang chạy: `ghcr.io/fevirtus/virtus-bot@sha256:12c39496e4c077c6d5b98bf8e22b2daf1c603e9c04a6f60d10763759782e933c`.
- [CI phát hành thành công](https://github.com/fevirtus/virtus-bot/actions/runs/35949224178): 44 kiểm thử; kiểm tra import thư viện legacy và compile đạt.
- Rollout thành công, 1/1 replica Ready, 0 lần restart tại thời điểm xác nhận. `/health/live` trả `alive`; `/health/ready` trả `ready`, kiểm tra cả Discord và PostgreSQL.
- Discord API xác nhận 9 slash commands tu tiên. Hai server đủ quyền có kênh game, 5 role cảnh giới và 2 bảng persistent mỗi server. Server thứ ba thiếu Manage Channels và Manage Roles: cần cấp quyền rồi chạy `/tutien_setup`.
- Hash các ID category/channel/role/panel/board trước và sau restart giống nhau: `c4f84773b743a42968be585c3d1a11161bf7f5461c3625ec7b4b8413dbb9fb5b`. Setup không tạo trùng tài nguyên trong lần kiểm chứng này.
- Smoke test dùng Discord API thật; chưa kiểm chứng bằng thao tác bấm của người chơi trên Discord client.
- Chuyển registry sang GHCR vì token Docker Hub cũ đã hết hạn. CI dùng `GITHUB_TOKEN` với quyền package phù hợp; package public và pull ẩn danh đã được xác nhận.
- Sửa thứ tự đăng ký health routes trước static mount; khóa dependency legacy `thefuzz` trong image. Startup chạy Python trực tiếp, không cài dependency bằng `uv` lúc khởi động.

## Quy trình rollback

Nếu bản mới không kết nối Discord/database hoặc không vượt readiness, đưa deployment về image cũ ở trên với `kubectl -n virtus-bot set image deployment/virtus-bot bot=<image-cũ>` và đổi đường dẫn của cả startupProbe, livenessProbe, readinessProbe về `/` trước khi theo dõi rollout: image cũ chưa có `/health/live` và `/health/ready`. Các bảng tu tiên thêm mới không cần xóa; dữ liệu tính năng cũ được giữ nguyên. Không restore backup đè lên dữ liệu mới chỉ để rollback code.

Backup local nằm trong thư mục riêng tư `/private/tmp/virtus-release`; chủ máy nên chuyển sang vị trí backup lâu dài phù hợp nếu cần giữ lâu. Script `backup_database.py` là logical snapshot các bảng ứng dụng, không phải bản sao toàn bộ role/extension/server PostgreSQL.

## Bản sửa trải nghiệm — 2026-09-24

Đang kiểm thử và chuẩn bị rollout; chưa coi thay đổi local là production. Phạm vi D033: giải thích tư chất, điều hướng cá nhân, bảng hoạt động bền vững, thưởng thực nhận và sửa hiệu ứng Nghịch Thiên. Bot hiện chỉ tham gia server được chủ bot yêu cầu giữ lại; không cần thiết lập lại các server đã rời. Mô phỏng 100 nhân vật sau sửa đạt Trúc Cơ trung bình 10,79 ngày (`balance/runtime-ux-fix-results.json`).
