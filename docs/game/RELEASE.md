# Phát hành tu tiên 1.0 — 2026-09-24

Trạng thái: đã hoàn thiện code và kiểm chứng trước phát hành; chờ image CI và rollout. Mục này sẽ cập nhật bằng kết quả thực tế, không coi test local là deployed.

- Hoàn tất các hạng mục thiếu của pilot; chi tiết ở IMPLEMENTATION.md và D032.
- 32 kiểm thử runtime/Discord adapter/PostgreSQL đạt, 9 kiểm thử mô hình lịch sử đạt; Python compile và kiểm tra whitespace đạt.
- Mô phỏng 100 nhân vật bằng runtime thực: Trúc Cơ trung bình 10,83 ngày, Kim Đan 32,62, Nguyên Anh 81,08, Hóa Thần 179,24. Seed, giả định và P10/P90 nằm trong `balance/runtime-results.json` và `scripts/simulate_runtime.py`.
- Backup nhất quán chỉ đọc qua pod đang chạy đã hoàn tất; không đưa backup hoặc secret vào Git/image. 7 bảng, 46.487 bản ghi cũ. Phục hồi vào PostgreSQL local và chạy startup migration hai lần, so sánh toàn bộ bản ghi: không thay đổi dữ liệu cũ.
- Production: namespace `virtus-bot`, deployment `virtus-bot`, container `bot`, replicas=1, strategy=Recreate. Dùng lại secret `virtus-bot-env` và database hiện tại, không tạo/reset database.
- Image trước phát hành: `fevirtus/virtus-bot@sha256:d67b288607ff1ef30cb5e72ad6ef7a4fc8ddaea42dd27d668c2e8d23de107bce`.
- CI mới chạy test với PostgreSQL trước publish; tag immutable `sha-<commit>`. Pull request không đăng nhập registry hoặc push image.

## Quy trình rollback

Nếu bản mới không kết nối Discord/database hoặc không vượt readiness, đưa deployment về image cũ ở trên với `kubectl -n virtus-bot set image deployment/virtus-bot bot=<image-cũ>` và theo dõi rollout. Các bảng tu tiên thêm mới không cần xóa; dữ liệu tính năng cũ được giữ nguyên. Không restore backup đè lên dữ liệu mới chỉ để rollback code.

Backup local nằm trong thư mục riêng tư `/private/tmp/virtus-release`; chủ máy nên chuyển sang vị trí backup lâu dài phù hợp nếu cần giữ lâu. Script `backup_database.py` là logical snapshot các bảng ứng dụng, không phải bản sao toàn bộ role/extension/server PostgreSQL.
