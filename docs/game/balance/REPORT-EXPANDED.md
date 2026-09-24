# Cân bằng mở rộng: Trúc Cơ khoảng 10 ngày

Ngày 2026-09-23 · Candidate-004 · EXPERIMENT, không phải bản game đã triển khai.

## Kết luận

Nhóm chơi vừa trong mô hình đạt Trúc Cơ trung bình **9,86 ngày**, trung vị **8,40 ngày**, P90 **16,39 ngày**. Mục tiêu mới khoảng 10 ngày đạt theo trung bình giả định; không có nghĩa mọi người đều đạt ở ngày 10.

Đề xuất đường tiến trình tích lũy: **Trúc Cơ ~10 ngày → Kim Đan ~30 ngày → Nguyên Anh ~78 ngày → Hóa Thần ~172 ngày**. Các mốc sau là đầu ra ứng viên cần kiểm chứng, không phải luật đã duyệt. Ngân sách sau Kim Đan đang dư nhanh; chưa nên dùng bảng giá này làm kinh tế cuối cùng.

## Bằng chứng và tái chạy

- [Mô hình và các giả định đầy đủ](MODEL-EXPANDED.md).
- [Cấu hình ứng viên hiện tại](candidate-004.json), [kết quả đầy đủ](result-004.json).
- [So sánh tắt cửa hàng/đan và tăng giá](sensitivity-004.json), [lưới combat](combat-004.json).
- [CSV tiến trình](progression-004.csv), [CSV kinh tế](economy-004.csv).
- [Script mô phỏng](../../../scripts/simulate_game_balance.py), [script thí nghiệm](../../../scripts/run_balance_study.py), [test](../../../scripts/test_game_balance.py).

```sh
python3 scripts/simulate_game_balance.py
python3 scripts/run_balance_study.py
python3 scripts/test_game_balance.py
```

Chạy 500 nhân vật × 5 hồ sơ, tối đa 240 ngày; 500 nhân vật × 4 kịch bản độ nhạy riêng đến Trúc Cơ trong 90 ngày; 72 kịch bản combat × 500 trận = 36.000 trận đối chứng. Seed cố định cho tái lập. Phân vị tính trên người hoàn thành và luôn đi kèm tỷ lệ hoàn thành. Kết quả tiền/nguyên liệu tại mốc là trung bình của người đã đạt mốc, không phải số dư ở cùng một ngày lịch.

## Các mốc theo hồ sơ

### Ít chơi

- Truc Co: trung bình 18.7 ngày; trung vị 17.44; P10–P90 11.47–26.42; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 18.7 ngày.
- Kim Dan: trung bình 66.13 ngày; trung vị 65.35; P10–P90 54.35–79.4; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 47.43 ngày.
- Nguyen Anh: trung bình 177.25 ngày; trung vị 177.36; P10–P90 158.35–197.42; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 111.11 ngày.
- Hoa Than: chưa có người đạt trong chân trời 240 ngày (0/500); không diễn giải là không bao giờ đạt.

### Chơi vừa, cá nhân

- Truc Co: trung bình 9.86 ngày; trung vị 8.4; P10–P90 5.42–16.39; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 9.86 ngày.
- Kim Dan: trung bình 30.04 ngày; trung vị 29.34; P10–P90 23.39–38.4; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 20.19 ngày.
- Nguyen Anh: trung bình 77.52 ngày; trung vị 76.49; P10–P90 67.54–88.41; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 47.47 ngày.
- Hoa Than: trung bình 171.94 ngày; trung vị 171.42; P10–P90 157.35–187.46; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 94.42 ngày.

### Chơi vừa, đội ba người

- Truc Co: trung bình 9.49 ngày; trung vị 8.37; P10–P90 5.38–15.39; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 9.49 ngày.
- Kim Dan: trung bình 30.19 ngày; trung vị 29.38; P10–P90 23.37–38.4; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 20.7 ngày.
- Nguyen Anh: trung bình 77.31 ngày; trung vị 76.44; P10–P90 68.37–88.45; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 47.11 ngày.
- Hoa Than: trung bình 172.49 ngày; trung vị 171.49; P10–P90 157.42–187.5; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 95.18 ngày.

### Chơi nhiều, dùng hết lịch tối đa

- Truc Co: trung bình 3.45 ngày; trung vị 3.33; P10–P90 2.39–5.39; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 3.45 ngày.
- Kim Dan: trung bình 10.15 ngày; trung vị 9.42; P10–P90 8.51–12.39; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 6.7 ngày.
- Nguyen Anh: trung bình 24.89 ngày; trung vị 24.41; P10–P90 22.43–27.41; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 14.74 ngày.
- Hoa Than: trung bình 52.56 ngày; trung vị 52.39; P10–P90 49.52–55.53; hoàn thành 100.0%. Thời gian thêm từ mốc trước trung bình 27.68 ngày.

### Chỉ sinh hoạt

- Truc Co: chưa có người đạt trong chân trời 240 ngày (0/500); không diễn giải là không bao giờ đạt.
- Kim Dan: chưa có người đạt trong chân trời 240 ngày (0/500); không diễn giải là không bao giờ đạt.
- Nguyen Anh: chưa có người đạt trong chân trời 240 ngày (0/500); không diễn giải là không bao giờ đạt.
- Hoa Than: chưa có người đạt trong chân trời 240 ngày (0/500); không diễn giải là không bao giờ đạt.

Nhóm chỉ sinh hoạt không kiếm core/linh vật boss nên không thể đại đột phá; vẫn nhận nguyên liệu sinh hoạt trong mô hình mới. Nhóm ít chơi chưa đạt Hóa Thần trong chân trời chạy, nên không dùng một con số trung bình giả cho nhóm này. Nhóm chơi nhiều tới Trúc Cơ khoảng 3,45 ngày: khoảng cách với nhóm vừa là rủi ro thiết kế cần quyết định, không được giấu bằng trung bình chung.

## Combat và độ nhạy

Đối chứng boss Luyện Khí tầng 5, tư chất chuẩn, không trọng thương; mỗi dòng 500 trận cùng danh sách seed. Đây là boss farm cơ bản, không phải tỷ lệ thắng cho mọi boss.

- Đội 1, attack, ngân sách 0 đan: thắng 63.6%, thời gian trung bình 72.39 giây.
- Đội 1, attack, ngân sách 1 đan: thắng 100.0%, thời gian trung bình 72.73 giây.
- Đội 1, balanced, ngân sách 0 đan: thắng 77.2%, thời gian trung bình 82.84 giây.
- Đội 1, balanced, ngân sách 1 đan: thắng 100.0%, thời gian trung bình 82.99 giây.
- Đội 1, careful, ngân sách 0 đan: thắng 100.0%, thời gian trung bình 90.97 giây.
- Đội 1, careful, ngân sách 1 đan: thắng 100.0%, thời gian trung bình 90.97 giây.
- Đội 3, balanced, ngân sách 0 đan: thắng 100.0%, thời gian trung bình 70.31 giây.

- Kịch bản baseline: trung bình 9.86 ngày; P90 16.39; hoàn thành 100.0% trong 90 ngày.
- Kịch bản no_shop: trung bình 11.17 ngày; P90 17.38; hoàn thành 100.0% trong 90 ngày.
- Kịch bản no_potions: trung bình 12.52 ngày; P90 22.42; hoàn thành 100.0% trong 90 ngày.
- Kịch bản expensive_shop: trung bình 9.86 ngày; P90 16.39; hoàn thành 100.0% trong 90 ngày.

Cửa hàng giúp nhóm vừa nhanh hơn khoảng 1,31 ngày; không có đan hồi máu vẫn tiến được nhưng chậm hơn khoảng 2,66 ngày. Tăng gấp đôi giá NPC chưa đổi tiến trình trong mẫu này vì nguồn tiền đủ; cần xét nguồn thu chứ không chỉ tăng giá shop.

Candidate-003 ban đầu làm kịch bản không đan hồi máu không có người lên Trúc Cơ trong 90 ngày; xem [thí nghiệm cũ](sensitivity-003.json). Candidate-004 giảm sát thương boss, cải thiện Thận trọng, giảm 10% XP Luyện Khí và đổi nhịp sang bảy giây. So sánh hai candidate là thay nhiều biến, không quy toàn bộ cải thiện cho riêng bảng XP.

Tỷ lệ thắng cao của nhóm mang đan/đội ba người cho thấy boss cơ bản đã an toàn, phù hợp nguồn vật liệu thường nhưng không đủ làm nội dung thử thách lâu dài. Cần thêm boss tinh anh/cơ chế khác trước khi cân bằng chiến thuật toàn diện. Thận trọng không đan đạt 100% trong mẫu boss này và chậm hơn Công kích; đó không phải bảo đảm bất bại.

## Tiền và nguyên liệu nhóm vừa

Số liệu tích lũy đến từng mốc, cộng thêm 150 linh thạch nhập môn khi tính số dư.

- Truc Co: thu 868.99, chi 491.61, còn 527.38 linh thạch; chi NPC 89.24; dùng 6.09 đan hồi máu trung bình.
- Kim Dan: thu 4211.25, chi 1410.81, còn 2950.44 linh thạch; chi NPC 112.38; dùng 17.38 đan hồi máu trung bình.
- Nguyen Anh: thu 16095.55, chi 3171.64, còn 13073.91 linh thạch; chi NPC 130.06; dùng 45.63 đan hồi máu trung bình.
- Hoa Than: thu 47378.52, chi 6166.52, còn 41362.00 linh thạch; chi NPC 146.38; dùng 102.28 đan hồi máu trung bình.

Tới Trúc Cơ: thu 51.88 Linh thảo từ hoạt động/sinh hoạt và mua thêm 15.74; thu 25.95 Linh tuyền và mua 5.25; thu 6.74 Yêu đan/core. Tiêu hao gộp 54.01 thảo, 23.22 tuyền, 4.11 core; các khoản hoàn thất bại được báo riêng trong JSON, không tính là nguyên liệu kiếm mới.

Cửa hàng đang bù nguyên liệu thường, không thay boss; chi NPC gần như bão hòa về sau. Ở Hóa Thần, nhóm vừa dư khoảng 41.362 linh thạch trong mô hình không có chi roll/tông môn/trang bị. Nguyên liệu cũng dư vì lượng công thức không tăng theo thời gian cảnh giới. Đây là dấu hiệu cần cân bằng tiếp: scale nguyên liệu/phí công thức cao cấp và thêm các chỗ tiêu tùy chọn đã được chốt trước khi kết luận kinh tế ổn định. Không đề xuất tịch thu tiền hoặc phí bảo trì để chữa dư thừa.

## Các giả định chưa được duyệt như luật game

Bảng XP/giá/drop/công thức, xác suất đại đột phá sau Trúc Cơ, thời gian đan, nguồn nguyên liệu sinh hoạt, giá/hạn mức NPC, kho nguyên liệu phân cảnh giới và hệ số combat đều còn là candidate. Đặc biệt: đồng đội cùng cấp giả lập, HP/linh lực hồi giữa chặng, kỹ năng đơn giản, công thức mở sẵn, một loại boss mỗi bậc và chính sách kiểm tra tiến trình khá chăm. Chưa mô phỏng toàn bộ thiên phú, roll trả phí, tặng đồ, kinh tế tông môn, sự kiện thưởng/phạt, trang bị hoặc hành vi cộng đồng thật. Xem MODEL-EXPANDED.md để tránh đọc số liệu như cam kết production.

## Khuyến nghị

Giữ candidate-004 làm baseline nghiên cứu vì đạt trung bình Trúc Cơ khoảng 10 ngày và không bắt buộc đan/cửa hàng. Dùng 10/30/78/172 ngày làm mốc đề xuất tiếp theo. Chưa deploy nguyên trạng: ưu tiên kiểm tra khoảng cách người chơi nhiều, kinh tế dư về cuối, hồi trạng thái giữa chặng và đa dạng boss. Chỉ sửa luật đã chốt sau khi có quyết định riêng; các thay đổi số liệu candidate tiếp tục lưu phiên bản để so sánh.
