# Trạng thái triển khai — 1.0.0

Ngày: 2026-09-24. Người dùng đã yêu cầu hoàn thiện và triển khai. Bản 1.0 hoàn tất các hạng mục thiếu liệt kê ở pilot; trạng thái phát hành và kiểm chứng live được ghi trong RELEASE.md. Tài liệu này phân biệt code đã có với đặc tả sản phẩm; không thay thế RULES.md hoặc tự chuyển thông số OPEN thành APPROVED.

## Tự thiết lập server

Khi bot kết nối hoặc vào server mới, cog `cultivation` tự tạo:

- Danh mục **Virtus · Tu Tiên**; ba kênh `tu-tien`, `thanh-tuu`, `tong-mon`.
- Năm role cảnh giới không có quyền quản trị; đồng bộ role theo hồ sơ.
- Bảng điều khiển có nút bền vững sau restart và lệnh `/tutien`.
- Trạng thái game mặc định trong PostgreSQL; không nhập ID kênh/role thủ công.

ID của tài nguyên được lưu ngay sau mỗi bước. Chạy `/tutien_setup` nhiều lần không tạo thêm bản sao; không chiếm tài nguyên cùng tên của server. Không tự xóa/sửa kênh hoặc role không do game quản lý. Kênh mới hiển thị cho mọi thành viên; kênh thành tựu mặc định chỉ bot gửi. Chủ server có thể chỉnh quyền Discord sau đó; bot không ghi đè lại quyền ở lần khởi động tiếp theo.

Yêu cầu ngoài khả năng tự thiết lập: **Message Content Intent** và **Server Members Intent** phải bật ở Developer Portal; token và PostgreSQL của ứng dụng phải hợp lệ. Role cao nhất của bot phải đứng trên role nó quản lý. Bot cần Manage Channels, Manage Roles, View Channel, Send Messages, Embed Links và Read Message History. Slash command cần scope `applications.commands` khi cài ứng dụng. Administrator không bỏ qua thứ bậc role.

Nếu Discord đã tạo tài nguyên nhưng mất kết nối trước khi lưu ID, bot dừng riêng quá trình setup để tránh tạo trùng. Quản trị viên kiểm tra tài nguyên vừa tạo rồi dùng `/tutien_doisoat resource_id:...`; lệnh chỉ nhận tài nguyên đúng loại/tên/dấu nhận diện. Không dùng quy trình này trong thiết lập bình thường. Nếu cần phục hồi một pending intent nhưng Discord thực tế chưa tạo tài nguyên, cần đối soát log/API trước khi xóa trường pending trong database; chưa có nút tự bỏ qua tình huống không chắc chắn này.

## Luồng đã có

- Hồ sơ tự tạo; XP chat có cooldown và chống lặp nội dung, voice cần từ hai người hợp lệ, loại bot/AFK/deaf. Mute vẫn tính. Hạn mức xã hội dùng chung, reset 04:00 giờ Việt Nam. Không bù voice lúc bot offline.
- Chín tầng, đột phá nhỏ thủ công, đột phá lớn tiêu vật phẩm và linh thạch; thất bại mất tu vi/trọng thương, cộng cảm ngộ. Roll cả bộ trước mốc đầu miễn phí, sau đó trả phí, cho xem/giữ bộ cũ.
- Thám hiểm offline; kỳ ngộ/kiếp nạn chỉ lộ sau lựa chọn, có lựa chọn rời đi an toàn.
- Luyện theo mẻ, một lò, trừ nguyên liệu/phí khi xác nhận, kết quả cố định được lưu trước timer; hoàn vật liệu/pity cho công thức đặc biệt.
- Combat auto có HP, mana, chí mạng, dao động sát thương, ngũ hành, thiên phú, chiến thuật, ba hướng tu, ngân sách đan. Phó bản hai chặng mang HP/mana còn lại sang chặng sau; giữ thưởng chặng đầu nếu thua boss. Hiện quyết toán toàn chuyến ở cuối, không gửi từng nhịp lên Discord.
- Lobby 2–4 người cùng đại cảnh giới; mỗi người bấm sẵn sàng chấp thuận chiến thuật/ngân sách, chủ đội xuất phát. Đổi đội xóa trạng thái sẵn sàng. Lobby hết hạn sau 30 phút.
- Túi, cửa hàng nguyên liệu giới hạn, tặng vật phẩm phổ thông bằng `/tutien_tang`, chặn vật phẩm khóa; không có chuyển tiền/chợ.
- Tông môn chung, đóng góp, phiếu nâng cấp, chủ server quyết định trong nhóm nhiều phiếu nhất, nhiệm vụ tuần, boss tích lũy sát thương chung, nhận thưởng có kiểm tra trùng.
- Bảng xếp hạng cảnh giới/cống hiến/hoạt động, hộp thư riêng, bật/ngừng tham gia.

Lệnh phụ: `/tutien_luyen`, `/tutien_bophieu`, `/tutien_nangcap`. Các thao tác chi tiêu từ hồ sơ đưa ra bản xem chi phí trước xác nhận. Quote cũ bị từ chối nếu điều kiện/chi phí thay đổi.

## Thông số pilot chưa phải kết luận cân bằng

Các mốc XP bắt đầu từ candidate-004. Runtime combat/tông môn khác mô hình cũ; bộ mô phỏng runtime bên dưới là nguồn kiểm chứng cho bản 1.0, kết quả 9,86 ngày cũ chỉ giữ làm lịch sử.

Những giá trị thử nghiệm nằm ở `services/cultivation/rules.py`, `engine.py`, `combat.py`: 150 linh thạch ban đầu, ba thám hiểm/ngày, năm lượt thưởng săn quái/ngày, hai phó bản/ngày, hai boss/tuần, cửa hàng 10 đơn vị/ngày, hiến 20 thảo/ngày, tặng 100 đơn vị/ngày. Thông số bản đầu cần tiếp tục đối chiếu telemetry thực tế.

Hiệu ứng công trình pilot: Đan phòng giảm 2% thời gian mỗi cấp (tối đa 10%); Dược viên cho tối đa 3 thảo/ngày; Tàng Kinh Các cho 5 XP nghề/ngày; Hộ Sơn giảm 2% sát thương nhận mỗi cấp (tối đa 10%). Tuần cần 100 cống hiến chung, người nhận có ít nhất 3; mục tiêu boss chung tính theo số thành viên như phần hoàn thiện bên dưới. Các giá trị này là phương án triển khai thử cho phần OPEN, không thay đổi luật đã chốt. Chưa khóa công thức bắt buộc sau công trình.

Đan đạt chuẩn/thượng phẩm: hồi phục 45%/55% HP; dưỡng thương rút 40%/50% thời gian ban đầu một lần; hộ mạch cộng 5/7,5 điểm phần trăm; đan đại đột phá thượng phẩm cộng 2,5 điểm phần trăm, luôn chặn ở 100%. Dùng đạt chuẩn trước rồi mới thượng phẩm; hoàn đúng chất lượng đan chưa dùng. Đan tăng tầng nhỏ và Tẩy Tủy chỉ một chất lượng. Lệnh tặng hỗ trợ chọn chất lượng/cảnh giới của stack.

## Phần hoàn thiện từ pilot

- Phó bản có một cửa sổ lựa chọn 60 giây sau chặng đầu, chủ đội đại diện chọn. Bỏ qua khi offline/an toàn; chỉ linh thạch kiếm ở chặng boss bị ảnh hưởng, không trừ túi riêng hoặc thưởng chặng đầu. Lựa chọn xuất hiện trong hồ sơ của đại diện, không yêu cầu cả đội bấm thêm. Kết quả được quyết toán cuối chuyến.
- Bảng tông môn bền vững tự cập nhật, hiện tiến độ boss/nhiệm vụ, thời điểm reset tuần và nút tham chiến/nhận thưởng. Boss mở cả tuần, không cần chủ server tổ chức thủ công. Mục tiêu khóa khi có trận đầu tuần: 500 × số nhân vật đang tham gia, tối thiểu 600, tối đa 10.000 sát thương chuẩn hóa.
- Tàng Kinh Các cấp 1 mở nghiên cứu Ngưng Thần Đan (50 linh thạch, học vĩnh viễn). Đan bổ sung tăng mana trận kế tiếp 10%/15%; không khóa đan đột phá bắt buộc. Luyện tốn 1 hoa + 2 nước và 15 × bậc cảnh giới linh thạch, 180 giây trước giảm thời gian của Đan phòng.
- Túi có phân trang, tìm kiếm, lọc cảnh giới/chất lượng, công dụng/nguồn kiếm/quyền tặng. Lệnh tặng chọn được cảnh giới và chất lượng của stack; hộp thư phân trang, không cắt mất kết quả.
- `/tutien_cauhinh` dành cho Manage Server: bật/ngừng game, bỏ qua/khôi phục XP kênh, gộp/tách bảng game. Gộp không xóa kênh cũ; tách dùng lại ID kênh riêng đã lưu. Kênh chat con kế thừa việc bỏ qua kênh cha.
- Đại đột phá và hạ boss tuần có thông báo công khai hiếm. Người chơi chủ động bật/tắt DM hoàn thành hoạt động; mặc định tắt. Outbox lưu cùng giao dịch phần thưởng; kiểm tra marker tin nhắn trước retry. Discord không cung cấp transaction chung với DB, vì vậy không hứa exactly-once tuyệt đối cho tin nhắn khi quá cửa sổ đối soát; tài sản trong DB vẫn chống lặp độc lập. DM bị chặn thì hộp thư giữ kết quả.
- Đã sửa giới hạn content Discord, lobby bị kẹt sau lỗi gửi, reset phiếu tuần khi không có đóng góp mới, chat xen kẽ nội dung để né cooldown, quote phí nâng cấp và vật phẩm khác cảnh giới, cùng độ khó quái để thăng tầng thực sự có lợi.

## Kiểm chứng cân bằng runtime

`python scripts/simulate_runtime.py --samples 100 --days 240 --output docs/game/balance/runtime-results.json` chạy chính `engine.execute`, crafting, combat, vật liệu và cửa hàng, không dùng thuật toán mô phỏng cũ. Lịch mẫu: xác suất hoạt động 4,5/7 ngày, 300–500 XP xã hội/ngày có hoạt động, 1–2 chuyến thám hiểm, 2 săn quái, 1 phó bản; người giả lập kiểm tra tiến trình ở 12 thời điểm cách nhau 30 phút. Nhân vật thật vẫn tự bấm luyện/đột phá, bot không tự chi tài nguyên.

100/100 đạt cả bốn mốc trong 240 ngày: trung bình Trúc Cơ 10,83; Kim Đan 32,62; Nguyên Anh 81,08; Hóa Thần 179,24 ngày. Trúc Cơ P10–P90: 6,19–17,19 ngày. Đây là kỳ vọng theo hành vi giả lập và RNG, không đảm bảo mỗi người mất đúng 10 ngày. Dư tiền cuối mẫu trung bình 40.004,78: linh thạch chủ yếu là chi phí phụ, chưa là nút thắt cuối game; không quảng cáo kinh tế dài hạn đã ổn định. Không có cơ chế trả tiền thật hoặc chuyển tiền để khai thác số dư này.

## Lưu trữ, phục hồi và kiểm thử

`cultivation_guilds` giữ trạng thái riêng theo server. Mỗi thay đổi khóa một hàng guild bằng PostgreSQL `FOR UPDATE`; `cultivation_receipts` lưu mã thao tác chống lặp trong cùng transaction. Lỗi giữa chừng rollback toàn bộ. Jobs chứa phiên bản, kết quả và hạn hoàn thành; tick 30 giây hoặc lần mở hồ sơ tiếp theo quyết toán đúng một lần sau restart. Kết quả đã cam kết vẫn về khi người chơi ngừng tham gia. Không lưu nội dung chat, chỉ hash chống lặp gần nhất.

Thiết kế khóa cả guild phù hợp cộng đồng bạn bè; không coi là kiến trúc cho hàng trăm nghìn người. Receipts chưa có chính sách lưu trữ/archival. Chạy một instance bot; khóa DB bảo vệ kinh tế nhưng chưa có bộ điều phối nhiều Discord gateway worker.

Bảng legacy vẫn được giữ nguyên, không đổi điểm cũ thành tài sản game. Startup tạo bảng trước migration legacy; migration không còn nuốt lỗi hoặc bỏ/tạo lại PK đúng trên mỗi lần chạy.

```sh
uv sync --frozen
uv run python -m unittest discover -s tests -v
uv run python -m unittest discover -s scripts -p 'test_game_balance.py' -v
# Chỉ đặt biến này trỏ đến database PostgreSQL kiểm thử riêng:
CULTIVATION_TEST_DATABASE_URL='postgresql+asyncpg://...' uv run python -m unittest discover -s tests -v
```

Database integration tests bỏ qua nếu không có URL kiểm thử. Bộ kiểm thử bao gồm chống double-spend đồng thời, rollback nguyên liệu, cô lập guild, XP voice không đếm trùng khoảng thời gian, quote hết hiệu lực, khôi phục crafting, pity, thưởng chặng đầu, reset và bootstrap Discord giả lập.

## Chạy bản code mới

Giữ cấu hình token/database đang dùng. File `.env.example` chỉ là mẫu cho môi trường mới. Không cần biến ID kênh/role của game. `uv run python main.py` chạy code này. Docker Compose hiện trỏ image `fevirtus/virtus-bot:latest`: image đó không tự chứa sửa đổi local; phải build/publish image mới rồi cập nhật deployment hiện có. Không chạy thêm bản bot thứ hai cạnh bản đang hoạt động khi kiểm thử live.

Kết quả kiểm chứng bản 1.0: 32 kiểm thử runtime/Discord mock/PostgreSQL và 9 kiểm thử mô hình lịch sử đều đạt; kiểm chứng phát hành cuối ở RELEASE.md. Kiểm tra riêng chạy migration hai lần giữ nguyên bản ghi cấu hình cũ đạt. Compile Python và `git diff --check` đạt. PostgreSQL dùng container tạm riêng, không dùng dữ liệu production. Không có kiểm thử Discord live hoặc triển khai image trong phiên này.
