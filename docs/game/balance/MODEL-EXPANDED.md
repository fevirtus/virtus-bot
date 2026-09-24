# Đặc tả mô hình thử nghiệm auto combat và kinh tế

Phiên bản nghiên cứu: candidate-004. Không phải đặc tả production đã duyệt.

## Phạm vi và lịch người chơi

Python standard library, hàng đợi sự kiện theo phút, chân trời 240 ngày. Ngày 0 là buổi đầu; một ngày mô hình bắt đầu lúc 04:00 giờ Việt Nam. Các ngày chơi được lấy mẫu độc lập; ngày đầu luôn chơi. Mỗi ngày chơi kéo dài bốn giờ với 24 đợt XP cách 10 phút. Đây là giả định hiện diện/kiểm tra game trong lúc sinh hoạt, không yêu cầu bấm liên tục suốt bốn giờ; mô hình tự thực hiện chính sách quyết định thay người dùng.

- Ít chơi: 3/7 ngày; 150–300 XP sinh hoạt trước giảm thưởng; một thám hiểm, một săn quái, một boss/phó bản.
- Vừa: 4,5/7 ngày; 300–500 XP; 1–2 thám hiểm, hai săn quái, một boss/phó bản.
- Vừa theo đội: cùng nhịp, đội ba người ở phó bản; hai đồng đội giả định cùng cảnh giới/tầng và sẵn sàng.
- Chạm trần: mỗi ngày; 1.800 XP thô cho ra tối đa 900 sau giảm thưởng; ba thám hiểm, năm săn quái, hai boss/phó bản.
- Chỉ sinh hoạt: lịch nhóm vừa, không đi hoạt động game. Có nguyên liệu sinh hoạt nhưng không có linh vật/core boss; không đạt đại đột phá, không thể kết luận mọi tầng nhỏ đều dễ đi chỉ bằng chat.

Không còn giới hạn một tầng/ngày. XP rải trong ngày, có thể lên nhiều tầng nếu đủ điều kiện và chuẩn bị đan. Khi đầy thanh mà chưa đột phá, XP dư mất do bể dự trữ chưa chốt. Kiểm tra tiến trình tại sự kiện; bắt đầu mẻ mới từ các mốc người chơi hoạt động, không tự nối vô hạn mẻ chỉ vì mẻ trước kết thúc. Đây là policy giả định tương đối chăm kiểm tra, không dự đoán hành vi thực của mọi người.

## Combat được tính từ trạng thái

Mỗi nhịp bảy giây. Chỉ số cơ sở trước tăng trưởng: HP 240, công kích 30, phòng ngự 12, linh lực 80. Hệ số sức mạnh theo cảnh giới 1/2/4/8, tăng theo tầng 7%. Phân bổ tư chất minh họa: công kích nhân q trong 0,95–1,05, HP nhân (2−q), giữ các chỉ số khác; đây chỉ là một họ phân bổ cân bằng, chưa bao phủ toàn bộ roll thiên phú/linh căn.

Sát thương = công kích × hệ số kỹ năng × random(0,9–1,1) × giảm giáp. Chí mạng 12%, hệ số 1,5. Giảm giáp chuẩn hóa theo sức mạnh cảnh giới để không làm trận kéo dài bất thường chỉ vì chỉ số tuyệt đối tăng.

Mỗi ba nhịp, đủ 15 linh lực thì dùng kỹ năng: sát thương 1,75 lần; Pháp tu thay bằng chữa người yếu và sát thương nhẹ. Thể tu tăng HP/giảm công kích và bảo vệ đồng đội; Kiếm tu tăng công kích. Trước Trúc Cơ là bộ kỹ năng nhập môn. Nhân vật chính ở các cảnh giới sau được gán Kiếm tu trong mẫu; đồng đội lần lượt Kiếm/Thể/Pháp. Chưa đại diện cho tất cả đội hình.

Quái thường: HP 155, công kích 20; boss: HP 390, công kích 22, rồi nhân hệ số cảnh giới/tầng. Mỗi bốn nhịp boss đánh diện rộng; ngoài ra chọn mục tiêu ngẫu nhiên, sát thương dao động và chí mạng. Boss đội tăng HP theo 1 + 0,78 × (số người − 1). Giới hạn quái 15 nhịp/boss 30 nhịp; quá giới hạn tính không thắng trong mô hình. Đây là giả định xử lý bế tắc chưa được chốt cho game.

Ba chiến thuật: Công kích tăng tấn công nhưng yếu phòng thủ/nhận sát thương nhiều hơn; Thận trọng giảm tấn công, tăng phòng thủ/giảm sát thương nhận; Cân bằng giữ cơ sở. Các hệ số nằm trong code/config, đều là candidate. Chưa có mô hình kháng khống chế, skill tree, trang bị, target priority phong phú hay boss nhiều dạng.

Đan hồi phục hồi 45% HP tối đa khi dưới 30%, ngân sách tối đa hai viên cho nhân vật chính toàn chuyến; không cấp lại ngân sách ở mỗi chặng. Chỉ dùng đan đã luyện và giữ riêng khi vào trận, trả phần chưa dùng. Đồng đội giả định không mang đan để tránh tạo tài nguyên miễn phí. Không trừ XP/trang bị khi thua. Có log đếm sát thương/hỗ trợ và vật phẩm dùng, kết quả từ cùng mô phỏng.

Phó bản gồm combat mở đầu, khoảng chuyển chặng/sự kiện 75 giây, boss. Policy bỏ qua sự kiện an toàn, không nhận thưởng sự kiện. Mô hình hiện hồi HP/linh lực giữa các chặng: giả định lạc quan chưa chốt, cần thử giữ trạng thái xuyên chặng trước production. Không có lobby chờ người thật, rút đội, hoặc phối hợp tài nguyên giữa các tài khoản thật. Không đổi cảnh giới trong chuỗi combat đang chạy.

## Nguyên liệu, đan và tiền

Kho nguyên liệu/đan chia theo cảnh giới đang farm: không cho đồ tầng trước tự thay công thức cảnh giới sau. Đây là giả định nội dung mở rộng; chưa phê duyệt toàn bộ SKU. Nguồn bắt buộc không bị khóa sau cảnh giới cần mở: công thức được giả định có đường học miễn phí khi vào cảnh giới tương ứng, chưa mô phỏng nhiệm vụ mở khóa.

- Mốc 200 XP sinh hoạt hợp lệ/ngày: hai Linh thảo, một Linh tuyền, tối đa một lần.
- Thám hiểm 20 phút: 3–5 Linh thảo, hai Linh tuyền và tiền/XP theo config. Một chuyến mỗi thời điểm; được thám hiểm đồng thời combat là giả định thử, chưa chốt luật sản phẩm. Nguyên liệu gắn cảnh giới lúc bắt đầu chuyến.
- Săn quái thắng: một Yêu huyết, tiền và XP.
- Boss thắng: một Yêu đan/core, một mảnh linh vật, 15% thêm nguyên món. Năm mảnh ghép một linh vật. Vẫn cấp mảnh nếu rơi nguyên món là giả định chưa chốt.
- NPC bán Linh thảo 4, Linh tuyền 5 linh thạch, tổng tối đa 10 đơn vị/người/ngày, mua đúng phần thiếu để bắt đầu mẻ. Không bán core/linh vật. Chỉ mua khi đủ toàn bộ giá mua + phí mẻ, không mua dở rồi thiếu tiền chế tạo. Chưa có giá tăng theo cảnh giới cho nguyên liệu NPC.

Công thức đại diện: đan tăng tầng dùng 2 thảo + 1 tuyền + phí 8; hồi máu 1 thảo + 1 huyết + phí 5; đan đại đột phá 8 thảo + 4 tuyền + 2 core + phí 50. Phí nhân 1/2/3/4 theo cảnh giới, lượng nguyên liệu chưa scale: đây là nguồn dư thừa về sau được báo trong kết quả. Một lò, phổ thông một phút, đan đại đột phá 10 phút. Thành công đại đan lần lượt 85/80/75/70%, bảo đảm sau hai thất bại; hoàn nửa từng nguyên liệu làm tròn xuống, không hoàn phí.

Policy ưu tiên đan tăng tầng/đại đột phá trước, chỉ luyện hồi máu khi tiền còn dự phòng nghi thức + 40. Mỗi lúc chuẩn bị đan cho bước tiếp theo, không luyện vô hạn tích trữ. Công thức cơ bản/đan hồi máu thành công chắc chắn. Chưa mô phỏng Tẩy Tủy Đan, Hộ Mạch Đan, Dưỡng Thương Đan hoặc phẩm chất/cấp nghề; do đó thu chi chưa bao gồm các khoản tùy chọn này.

Khởi đầu 150 linh thạch một lần. Thu nhập cơ bản: thám hiểm 25, quái 12, boss 55; nhân 1/2/3/4 theo cảnh giới. Nghi thức 80/160/240/320. Có kiểm tra bảo toàn tiền sau mỗi sự kiện: tiền hiện tại = tiền nhập môn + thu − chi. Không nhận lại vật phẩm từ retry hoặc bán đồ.

## Đột phá và chậm dần

Candidate-004 yêu cầu tổng XP từng cảnh giới: bảng chính xác trong JSON. Luyện Khí giảm 10% so với candidate-003; các cảnh giới sau theo hệ số XP 2,5/6/12 của bảng cơ sở trước giảm. Thưởng XP hoạt động không tăng cùng hệ số, vì vậy thời gian từng cảnh giới tăng dần.

Tiểu đột phá chắc chắn, dùng 1/2/3 viên như luật đã duyệt. Đại đột phá cần XP đầy + đan + linh vật + tiền; thất bại mất 10% thanh tầng 9, trọng thương 6/12/24/24 giờ. XP bị giảm nửa trong thương tích, công kích giảm 20% như một cách diễn giải tạm thời của hiệu quả chiến đấu −20% (chưa phải công thức chính thức). Chặn đột phá khi trọng thương.

Xác suất ban đầu đến Trúc Cơ/Kim Đan/Nguyên Anh/Hóa Thần: 50/45/40/35%; cảm ngộ mỗi thất bại +15/+12,5/+10/+10 điểm phần trăm, trần 100%. Chỉ Trúc Cơ là số đã chốt trước; các số cảnh giới sau là đề xuất mô phỏng.

## Giới hạn và kiểm chứng

Không có tặng đồ thật, kinh tế tông môn, roll trả phí, trang bị, toàn bộ thiên phú/linh căn, sự kiện có phần thưởng hoặc đồng đội chênh cấp. Không giả định những hệ này không ảnh hưởng kết quả. Người dùng tương tác ít hơn policy sẽ lên chậm hơn. Không mô phỏng cộng đồng có lượng người online biến động hoặc chiến lược tối ưu của người chơi.

Phân vị chỉ tính người đạt mốc; luôn báo tỷ lệ hoàn thành/censored. Điểm blocked_checks là số lần policy gặp điều kiện thiếu, không phải số ngày bị kẹt hoặc phân tích nhân quả. Tỷ lệ thắng 100% trong mẫu hữu hạn không phải bảo đảm thắng ở production. Không gán tỷ lệ 0% cho nhóm không có trận như thất bại thực; dữ liệu raw có attempts để phân biệt.

Test mô hình bao gồm tái lập, sổ tiền, tồn kho không âm, ngân sách đan, cửa hàng, nhiều tầng/ngày, trọng thương, pity luyện đan/đột phá và hoàn thành mẻ offline. Không thay thế kiểm thử bot, DB, Discord hoặc kiểm chứng gameplay với người thật.
