# Mô phỏng sơ bộ Luyện Khí → Trúc Cơ

Báo cáo lịch sử. Mục tiêu 2–3 tuần đã được thay bằng khoảng 10 ngày; xem [báo cáo mở rộng](REPORT-EXPANDED.md).

Ngày: 2026-09-23. Trạng thái: EXPERIMENT, chưa phải kiểm chứng cân bằng production.

## Tái chạy

Từ root repo, Python 3.9+ standard library; không đọc token, không truy cập DB/Discord:

```sh
python3 scripts/simulate_progression.py
python3 scripts/simulate_progression.py --config docs/game/balance/candidate-002.json --output docs/game/balance/result-002.json
```

- [Script](../../../scripts/simulate_progression.py)
- [Candidate 001](candidate-001.json) và [kết quả 001](result-001.json)
- [Candidate 002](candidate-002.json) và [kết quả 002](result-002.json)

Mỗi cấu hình chạy 2.000 nhân vật/hồ sơ, bốn hồ sơ, tối đa 120 ngày. Cùng seed gốc để tái lập; RNG tiêu thụ khác nhau khi tiến trình khác nên không coi các lần chạy là cặp hành vi hoàn toàn giống nhau. Ngày tính từ lần đăng nhập đầu (ngày 0); phân vị chỉ tính người hoàn thành, luôn kèm tỷ lệ hoàn thành để tránh che các trường hợp chưa đạt.

## Giả định và phạm vi

- Ít chơi: xác suất hoạt động 3/7 mỗi ngày, 150–300 XP sinh hoạt, 1 thám hiểm, 1 săn quái, 1 boss trong ngày chơi.
- Vừa: xác suất 4,5/7, 300–500 XP sinh hoạt, 1–2 thám hiểm, 2 săn quái, 1 boss.
- Chạm trần: mỗi ngày 900 XP sinh hoạt, 3 thám hiểm, 5 săn quái, 2 boss.
- Chỉ sinh hoạt: cùng lịch nhóm vừa, không hoạt động game. Mô hình CHƯA cấp nguyên liệu sinh hoạt/NPC/tặng nên bị kẹt ngay tầng đầu; không dùng kết quả này làm kết luận rằng thiết kế thật chặn tầng nhỏ. Luật thật vẫn cần linh vật boss để đại đột phá.
- Ngày đầu luôn hoạt động; một phiên mỗi ngày chơi, giờ bắt đầu ngẫu nhiên. Nguyên liệu/công thức có sẵn đường tiếp cận giả định; nhận thưởng hoạt động gộp trong phiên.
- Mỗi phiên tối đa một lần tăng tầng; XP vượt thanh hiện tại không dự trữ. Đây là giả định bảo thủ do bể dự trữ còn chưa chốt; nó làm nhóm nhiều chơi chậm hơn lịch nhận XP rải trong ngày.
- Nguyên liệu và tiền là kho thật trong mô hình, bị trừ/hoàn theo công thức candidate. Linh vật rơi 10% và mỗi boss thắng cấp một mảnh; năm mảnh ghép được một món, kể cả khi đã rơi nguyên món. Chi tiết drop này là giả định chưa duyệt.
- Boss thắng cố định 85%, quái thường coi hoàn thành; chưa mô phỏng sức mạnh, đan combat, trọng thương giảm chiến lực hoặc khó dần. Chưa phải mô phỏng chiến đấu.
- Luyện đan phổ thông chắc chắn, đặc biệt 80%, bảo đảm sau hai thất bại; hoàn nửa nguyên liệu làm tròn xuống, không hoàn tiền. Công thức/giá mới là giả định, không thay luật hiện hành.
- Đột phá theo xác suất/cảm ngộ và mất 10% thanh tầng 9 đã duyệt. Trọng thương sáu giờ có trong trạng thái nhưng lịch một phiên/ngày hầu như tránh được hình phạt; chưa đo tác động giảm XP trong sáu giờ ngay sau thất bại. Không retry liên tục trong phiên.
- Phút luyện cộng vào thời điểm hành động, không mô hình đầy đủ hàng đợi offline hoặc khoảng chờ giữa từng lượt combat. Không mất tiến trình bởi mô phỏng thời gian chờ; chỉ là xấp xỉ.
- Chưa có thiên phú, NPC, tặng đồ, tông môn, chất lượng đan, tiền roll tư chất, các lần rơi vật phẩm sinh hoạt hoặc sự kiện. Nhóm vừa có hai lượt săn quái giả định, cần so với hành vi thực.

## Kết quả

Tất cả nhóm ít/vừa/chạm trần hoàn thành trong 120 ngày ở cả hai candidate. Nhóm chỉ sinh hoạt 0/2.000 hoàn thành vì giới hạn mô hình nêu trên.

- Ít chơi: trung vị candidate-001 45.43 ngày → candidate-002 37.65 ngày. Candidate-002 P10/P90: 28.64/48.78 ngày; đạt trước ngày 21: 0.35%.
- Chơi vừa: trung vị candidate-001 21.92 ngày → candidate-002 19.68 ngày. Candidate-002 P10/P90: 15.49/25.55 ngày; đạt trước ngày 21: 64.45%.
- Chạm trần: trung vị candidate-001 10.36 ngày → candidate-002 10.36 ngày. Candidate-002 P10/P90: 9.43/12.37 ngày; đạt trước ngày 21: 100.0%.

## Diễn giải

Candidate-002 chỉ hạ yêu cầu XP các tầng sau: tổng 4.900 → 3.850; không sửa xác suất/thua/hoàn nguyên liệu hoặc giá giữa hai lần chạy. Nhóm vừa tiến gần mục tiêu 2–3 tuần, nhưng P90 vẫn hơn ba tuần. Đây là độ nhạy với bảng XP trong lịch một phiên/ngày, không chứng minh candidate-002 đã cân bằng tối ưu.

Việc nhóm chạm trần không đổi thời gian dù hạ XP cho thấy giới hạn tăng một tầng/phiên và lịch nhận nguyên liệu ảnh hưởng kết quả; không nên dùng khoảng 10 ngày đó làm tốc độ tối thiểu của game thật. Nhóm chỉ sinh hoạt cần được mô phỏng lại với nguồn nguyên liệu sinh hoạt trước khi đánh giá tính khả thi.

Chưa mô phỏng Kim Đan, không khẳng định mục tiêu 6–8 tuần đã đạt. Không kết luận thiếu nguyên liệu/tiền không xảy ra chỉ vì bộ giá thăm dò đang đủ. Bộ đếm blocked_visits chỉ đếm các điều kiện kiểm tra thất bại của mô hình, không phân tích nhân quả đầy đủ.

## Việc còn lại

1. Thay gộp XP cuối phiên bằng lịch sự kiện trong ngày, kiểm tra XP tại thời điểm đầy thanh và đột phá.
2. Thêm vật phẩm sinh hoạt, NPC và thời gian/chi phí combat, cùng lịch thương tích thực.
3. Mô phỏng các bảng giá/công thức và mức tham gia khác nhau; báo phân vị/tỷ lệ chưa hoàn thành, không chỉ trung bình.
4. Mở tiến trình Trúc Cơ → Kim Đan khi có công thức, xác suất và phần thưởng tương ứng; không tự sao chép tỷ lệ Trúc Cơ.
5. Chỉ đề xuất khóa bảng số sau các kiểm chứng trên; hai candidate hiện vẫn PROPOSED_SIMULATION_ONLY.
