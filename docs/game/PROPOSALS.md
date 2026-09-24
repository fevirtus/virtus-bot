# Đề xuất và câu hỏi chưa chốt

Toàn bộ nội dung file này là PROPOSED hoặc OPEN, không được coi là yêu cầu đã duyệt chỉ vì đã lưu vào repo. Tham chiếu luật chuẩn tại [RULES.md](RULES.md).

## XP-P01 [OPEN] Thông số sinh hoạt

Giá trị XP/cooldown/ngưỡng/reset đã chuyển sang BALANCE-001. Cần chốt bộ lọc tin trùng/lệnh/attachment, loại trừ channel, phần lẻ và thứ tự áp trọng thương/cap, phục hồi phiên voice.

## REALM-P01 [OPEN] Nội dung và đường cong tiến trình

Lộ trình đề xuất: Phàm Nhân → Luyện Khí → Trúc Cơ → Kim Đan → Nguyên Anh → Hóa Thần → Luyện Hư → Hợp Thể → Đại Thừa → Độ Kiếp. Cần khóa tên, bảng tu vi, phạm vi phát hành đầu và điều kiện nhập môn. Mục tiêu mới Trúc Cơ trung bình khoảng 10 ngày theo BALANCE-003; các mốc sau đang được mô phỏng lại, xem balance/REPORT-EXPANDED.md.

Bể tu vi chờ đột phá từng được đề xuất ở mức 20% nhưng chưa duyệt sự tồn tại/kích thước. Hộ pháp từng đề xuất tối đa hai người, mỗi người +5 điểm phần trăm; số liệu chưa duyệt. Khoản chờ thử lại 6 giờ riêng chưa chốt; không cộng thêm lên trọng thương mặc định.

## GEN-P01 [PROPOSED] Bộ tư chất và roll lại

Cấu trúc bộ và quyền roll hiện đã chuyển sang GEN-001/002 trong RULES. Phần còn đề xuất: linh căn thuộc Kim/Mộc/Thủy/Hỏa/Thổ; hai thiên phú không trùng và tương thích; chưa thêm song linh căn/biến dị ở bản đầu. Xác suất, hiệu ứng và độ hiếm phải công khai trước roll.

Ví dụ thiên phú để thảo luận: Kiếm Tâm tăng tỉ lệ chí mạng; Dược Duyên tăng cơ hội tiết kiệm nguyên liệu; Phúc Tinh thiên về kỳ ngộ; Nghịch Thiên tăng trần lợi ích kèm áp lực kiếp nạn. Đây không phải bộ dữ liệu đã cân bằng. Không có thiên phú vô dụng hoặc tổ hợp khóa đường chơi; lợi ích/xác suất/đánh đổi cần bảng cấu hình trước triển khai.

Đề xuất kỹ thuật: lưu kết quả đang chờ chọn để reconnect không tạo roll mới ngoài ý muốn. Roll không cấp vật phẩm hoặc thưởng kinh tế. Không giới hạn số lượt miễn phí bằng hạn mức ngày; chống request trùng hoặc quá tải không được biến thành giới hạn tiến trình.

Mốc kết thúc roll miễn phí đã chốt tại BALANCE-003. Màn hình đột phá phải báo chuyển sang roll trả phí trước xác nhận. Thao tác roll/khóa xử lý nguyên tử để tránh race.

Mốc trên chỉ kết thúc roll miễn phí, không khóa vĩnh viễn quyền đổi tư chất. Các phương án hạn mức cũ đã bị thay thế tại D008. Khi hỗ trợ roll trả phí, màn hình đột phá phải mô tả đúng việc chuyển sang trả giá.

Nếu cho đổi thiên phú trước khóa, hiệu ứng nghề/kinh tế phải tránh việc roll để nhận lợi ích một lần rồi đổi; cân nhắc chỉ kích hoạt các hiệu ứng đó sau khóa. Không làm mất thưởng đã hợp lệ.

## GEN-P02 [PROPOSED] Chỉ số khởi đầu và duyên/nạn

Ngân sách cân bằng đã chốt tại GEN-003. Phần còn đề xuất: dao động 90–110% mức cơ sở từng chỉ số, tổng độ lệch chuẩn hóa bằng 0. Cần chọn thuật toán lấy mẫu và làm tròn sao cho giữ ngân sách; chưa chốt dải roll.

Vai trò Phúc duyên và Kiếp số đã chốt tại GEN-004. Cần chốt phân phối tương quan và công thức tác động đến kết quả ẩn sau lựa chọn (EVENT-002).

Tách tư chất với trạng thái sự kiện theo GEN-006. Cần chốt dải, phân phối tương quan, hệ số và sàn/trần xác suất. Không mặc định dùng cùng ngân sách chiến đấu cho hai chỉ số duyên/nạn.

## GEN-P03 [PROPOSED] Roll trả phí và bảo toàn tiến trình

Chi phí và thời điểm trả đã chốt tại GEN-005; bảo toàn tiến trình tại GEN-006. Còn OPEN: công thức, nguồn đan, giá và thời gian chờ.

Đề xuất kỹ thuật: mỗi lần chỉ có một bộ chờ quyết định, không tích trữ nhiều bộ để ghép/chuyển tự do.

Đề xuất bổ sung: không hồi linh lực bằng roll, cấm roll khi đang xử lý một sự kiện đã khóa kết quả. Khi sinh lực tối đa đổi, cần chốt giữ tỉ lệ hay giữ lượng máu hiện tại có giới hạn; không mặc định hồi đầy.

Đề xuất thực hiện trừ giá, lưu kết quả và chuyển trạng thái nguyên tử với mã yêu cầu chống trùng; restart không trừ tiền lần hai hoặc reroll kết quả. Những chi tiết kỹ thuật trong mục này còn chờ duyệt, không thay đổi phần đã chốt ở GEN-005/006.

## COMBAT-P01 [OPEN] Chi tiết chuẩn bị auto combat

Luật chiến thuật/ngân sách và đội ở COMBAT-002/003. Cần chốt hệ số lợi/hại ba chiến thuật, ưu tiên dùng kỹ năng và đan. Hai viên Hồi Xuân Đan, ngưỡng máu 30% chỉ là ví dụ chưa khóa.

Đề xuất giữ riêng số đan đã mang để không dùng/tặng trùng; ngân sách áp dụng toàn phó bản, không cấp lại mỗi chặng. Đề xuất khóa danh sách/cấu hình khi bắt đầu; đổi mục tiêu/độ khó trước đó làm mất xác nhận sẵn sàng. Cần chốt giới hạn chênh cấp/carry và cơ chế đổi cấu hình đã lưu, không tự tăng chi phí đã cho phép.

## COMBAT-P02 [OPEN] Công thức và tính nhất quán auto combat

Luật mô phỏng, hiển thị và khung thời gian ở COMBAT-004/005. Cần chốt công thức sát thương, ưu tiên mục tiêu, hồi chiêu, linh lực giữa các chặng, hồi sinh, chống khống chế vô hạn, khi nhân vật ngã, rút lui, hòa và giới hạn thời gian cứng. Chưa thêm thuộc tính tốc độ thứ năm. Không bổ sung hành động tay bắt buộc từng nhịp.

Đề xuất snapshot phiên bản luật, đội hình, tư chất/trạng thái, chiến thuật và nguồn lực khi bắt đầu. Thương tích/buff hết hạn giữa trận cần luật rõ. Lưu seed/kết quả RNG phía server, không lộ seed tương lai; restart/reconnect không đổi kết quả, trừ tài nguyên hoặc phát thưởng lại. Cần chính sách bù lỗi dựa trên sổ giao dịch, không coi lỗi bot là thua.

Đề xuất báo cáo có đóng góp sát thương/bảo vệ/hỗ trợ, điểm ngoặt RNG, đan đã dùng và thưởng/lượt còn lại; chi tiết tài nguyên cá nhân riêng tư. Bảng số liệu, tần suất sửa thông báo và thời gian chờ sự kiện trong khung phó bản cần thiết kế cụ thể.

## EVENT-P01 [PROPOSED] Kỳ ngộ

Kỳ ngộ là sự kiện có lựa chọn, không chỉ một lần nhận quà. Nguồn: mốc sinh hoạt hợp lệ, thám hiểm, kết thúc phó bản. Roll theo cơ hội bị giới hạn, không roll mỗi tin nhắn/phút voice. Mặc định gửi riêng hoặc đưa vào hộp sự kiện để không spam channel.

Ví dụ tình huống trung tính: gặp người lạ, nghe tiếng gọi trong động phủ hoặc nhặt tàn quyển. Gợi ý, ẩn kết quả và bỏ qua không phạt đã chốt tại EVENT-002–004; phần kỹ thuật còn mở tại EVENT-P03.

Cơ hội hiếm có bảo đảm tiến triển sau nhiều lần không trúng; số lượt bảo đảm chưa chốt. Một số kỳ ngộ có thể hỗ trợ hồi phục sau chuỗi thất bại nhưng không trả lại toàn bộ chi phí và không thưởng thêm chỉ vì cố tình thất bại. Không cho bước nhảy trực tiếp qua điều kiện đại cảnh giới.

OPEN: tần suất, trọng số, thời hạn nhận, vật phẩm/phần thưởng và tác động của thiên phú.

## EVENT-P02 [PROPOSED] Kiếp nạn và cân bằng rủi ro

Đề xuất áp lực kiếp nạn tích lũy từ lựa chọn nguy hiểm, công pháp/thiên phú có đánh đổi hoặc các mốc tiến trình; không tích lũy chỉ vì chat/voice nhiều. Thiên phú mạnh có thể đi kèm rủi ro được công khai, không bí mật giảm may mắn để cân bằng.

Không báo trước nhánh cụ thể sẽ dẫn tới nạn (EVENT-002). Sau khi lựa chọn làm lộ một kiếp nạn dạng combat, đề xuất có bước chuẩn bị dùng đan/nhờ hộ pháp trước trận. Việc hiển thị áp lực tổng quát, thời hạn chuẩn bị và xử lý quá hạn còn OPEN; không tự áp hình phạt offline.

Ba chủ đề đề xuất: tâm ma (lựa chọn/thử thách), phản phệ (đánh đổi hiệu quả tạm thời), thiên kiếp (auto combat theo COMBAT-001). Phạm vi hậu quả tuân thủ EVENT-005: không mất XP/trang bị vĩnh viễn do sự kiện thường. Giá trị thưởng/phạt, thời gian và luật kiếp nạn lớn chưa chốt.

Không mặc định thêm một lần mất 10% tu vi/trọng thương lên hình phạt đại cảnh giới. Nếu thiên kiếp là bước của đại đột phá, phải có duy nhất một chuỗi kết quả và một lần quyết toán. Nếu là sự kiện riêng, hiển thị riêng và không kích hoạt khi đang trọng thương; cooldown bảo vệ chưa chốt.

Khuyến nghị dùng kiếp nạn để tạo lựa chọn rủi ro–lợi ích, không xóa sạch lợi thế của roll hiếm hoặc trừng phạt người hoạt động tích cực. Thắng kiếp không hoàn toàn bù mọi chi phí để tránh chủ động farm chuỗi thất bại.

OPEN: kiếp nạn độc lập hay tích hợp đột phá; nguồn áp lực; giới hạn phạt; chu kỳ và quyền hoãn.

## EVENT-P03 [PROPOSED] Tình huống ẩn và mức hậu quả

Khung lựa chọn, cách ẩn kết quả, tác động tư chất, bỏ qua và giới hạn hậu quả đã chuyển sang EVENT-002–005. Phần còn đề xuất: mỗi sự kiện có 2–3 lựa chọn, không khẳng định sai rằng nhánh nguy hiểm là an toàn. Ví dụ người lạ bán hộp gỗ: kiểm tra phù văn, mở hộp, hoặc rời đi.

Đề xuất kỹ thuật: chuẩn hóa trọng số, áp sàn/trần và kiểm tra để hai chỉ số không vô tình triệt tiêu nhau. Chưa chốt công thức, bảng tỉ lệ hoặc việc trạng thái áp lực ảnh hưởng thế nào đến lựa chọn.

Đề xuất snapshot tư chất lúc mở sự kiện để không đổi bộ trước chọn nhằm đổi bảng kết quả. Thời điểm snapshot, thời hạn nhận và việc khóa roll khi có sự kiện chờ vẫn cần chốt. Lưu kết quả đã xác định và chống bấm lại tuân thủ EVENT-003.

Đề xuất công khai phạm vi hậu quả chung trong hướng dẫn dù nhánh kết quả cụ thể bị ẩn. Không đưa mất tu vi vào sự kiện thường vì đã bị loại tại EVENT-005. Luật rút lui khỏi trận chiến sự kiện còn OPEN.

Đề xuất nội dung nguy hiểm hơn cần một lần xác nhận nhận thử thách sau khi lộ tình huống, vẫn không tiết lộ kết quả cuối cùng. Không mặc định áp dụng cơ chế giấu thông tin cho màn hình đột phá: BREAK-003 giữ nguyên.

## ITEM-P01 [OPEN] Chi tiết túi đồ và công thức

Luật đã chốt tại ITEM-001/002. Còn đề xuất: phân trang UI, trang bị tương lai có định danh riêng, vật phẩm công thức tiêu hao khi học thành công. Cần chốt xử lý công thức trùng, lỗi nhận vật phẩm, xác nhận thao tác và giới hạn lưu trữ kỹ thuật nếu có; không được biến thành giới hạn ô chưa được duyệt.

## ITEM-P02 [OPEN] Phẩm cấp vật phẩm

Danh mục khởi đầu đã chốt tại ITEM-003. Còn đề xuất: phẩm cấp thể hiện chất lượng, tách khỏi cảnh giới và độ hiếm rơi. Cần chốt phẩm cấp từng loại, mã vật phẩm và công thức; không tự tạo mọi tổ hợp chất lượng cho mọi nguyên liệu.

## ITEM-P03 [OPEN] Sản lượng nguyên liệu

Nguồn chủ động đã chốt tại ITEM-004. Còn OPEN: tỉ lệ rơi, số lượt nhận thưởng, sản lượng mỗi nguồn, chống farm và nguồn thu linh thạch. Cần đối chiếu với chi phí tăng tầng/luyện đan trước khi khóa số liệu.

## ITEM-P04 [OPEN] Chuyển giao và xử lý giao dịch

Quyền tặng và nhóm khóa đã chốt tại ITEM-005. Cần xác định SKU đan phổ thông, hạn mức tặng/chống tài khoản phụ và kế thừa khóa khi chế tạo. Đề xuất: xem trước vật phẩm/số lượng/người nhận; trừ/cộng nguyên tử, có lịch sử và chống nhận trùng/restart. Không mở rộng thành chợ hoặc chuyển linh thạch khi chưa có quyết định mới.

## ALCHEMY-P01 [OPEN] Công thức và nhập môn chi tiết

Luật tại ALCHEMY-001/002. Còn OPEN: lượng nguyên liệu/linh thạch từng công thức, đường mở và XP cấp nghề, cách xử lý công thức trùng. Phải bảo đảm người ở Luyện Khí có thể tự luyện công thức bắt buộc để lên Trúc Cơ. Chưa mở dịch vụ luyện hộ.

## ALCHEMY-P02 [OPEN] Thời gian và xử lý mẻ

Khung mẻ tại ALCHEMY-003. Ví dụ chưa chốt: tối đa 10 viên/mẻ, phổ thông 1 phút/viên, đặc biệt 10 phút/viên. Cần chốt hàng chờ và hủy mẻ; không cho hủy để roll lại kết quả. Đề xuất lưu snapshot toàn bộ công thức và trạng thái tại lúc bắt đầu, khôi phục theo giờ thực và chống trừ/phát thưởng hai lần khi restart. Đề xuất giữ luật cũ cho mẻ đang chạy khi điều chỉnh cân bằng.

## ALCHEMY-P03 [OPEN] Tỉ lệ luyện và phân loại đan

Phương án B đã chốt ở ALCHEMY-004; A không còn là phương án đang chờ chọn. Cần phân loại Hộ Mạch Đan, xác suất nền, bonus nghề/thiên phú, quy tắc hoàn khi có tiết kiệm nguyên liệu và giới hạn xác suất. 80% chỉ là số để mô phỏng, chưa duyệt. Tính cả rủi ro luyện đan và đại đột phá khi cân bằng thời gian tiến triển.

## ALCHEMY-P04 [OPEN] Hiệu lực và XP nghề

Luật chất lượng ở ALCHEMY-005. Cần chốt hiệu lực cơ bản/thượng phẩm từng loại, phân phối chất lượng, XP khi hoàn tất, XP thất bại và mức giảm XP từ công thức thấp cấp. Quyền tặng theo ITEM-005; không tự coi mọi đan là phổ thông. Không buộc người chơi phụ thuộc người nghề cao cho công thức tiến trình bắt buộc.

## ACTIVITY-P01 [OPEN] Thám hiểm chi tiết

Luật đã chốt ở ACTIVITY-001. Cần chốt địa điểm/sản lượng/giá, một chuyến 15–30 phút là ví dụ chưa duyệt. Việc thám hiểm đồng thời săn quái/phó bản còn OPEN; chat/voice/luyện đan đồng thời đã được duyệt. Sự kiện không chặn thưởng cơ bản.

## ACTIVITY-P02 [OPEN] Săn quái chi tiết

Luật ACTIVITY-002 và COMBAT-001. Cần chốt danh mục quái, bảng thưởng, độ khó, giới hạn mở trận cá nhân khi đang trong đội và kỹ năng nhập môn tự động. Không dùng mô hình săn quái thủ công từng lượt nữa.

## ACTIVITY-P03 [OPEN] Phó bản và sự kiện đội

Khung đội, ba chặng và đường boss cá nhân đã duyệt ở ACTIVITY-003. Cần chốt mức thưởng/độ khó đường cá nhân so với đội, chống carry quá chênh cấp và ngưỡng đóng góp phù hợp auto. Không đánh giá đóng góp bằng số lần bấm hoặc thời gian online khi trận đang chạy.

Sự kiện đại diện/quá hạn đã chốt ở ACTIVITY-005. Cần chốt cách chọn đại diện, phạm vi ảnh hưởng, quyền đổi đại diện và người rời đội. Cửa sổ 30 giây là ví dụ chưa duyệt. Không mặc định bot tự chọn nhánh may/rủi khi tất cả offline.

## ACTIVITY-P04 [OPEN] Hạn mức và bảo toàn kết quả

Khung hạn mức và luật thua ở ACTIVITY-004. Cần chốt số lượt/reset/bù ngày nghỉ. Đề xuất lượt không thưởng không tăng bộ đếm mảnh bảo đảm hoặc tạo phần thưởng kinh tế qua sự kiện; không gây giảm thưởng của đồng đội còn lượt. Trừ lượt tối đa một lần mỗi chuyến, giữ tiến trình khi reconnect; bỏ dở rồi mở chuyến mới không cho nhận lại thưởng cũ miễn lượt. Cần mô phỏng để chặng đầu không thành cách farm vượt toàn phó bản.

Sự cố bot xử lý riêng với thua trận: khôi phục hoặc hoàn phần chi phí/lượt chưa được hưởng dựa trên lịch sử; chính sách cụ thể chưa chốt. Auto combat không bắt người chơi online để giữ quyền nhận thưởng.

## SECT-P01 [OPEN] Thiết lập tông môn

Khung một tông môn chung đã chốt tại SECT-001. Cần chốt cấu hình tên/biểu tượng, quyền thay đổi, chính sách nhân vật rời server/quay lại và cách lưu thành tích. Không mở phe cạnh tranh/PvP hoặc cấp quyền Discord qua chức danh game.

## SECT-P02 [OPEN] Công trình và định lượng đóng góp

Khung công trình/đóng góp tại SECT-002. Cần chốt chi phí, cấp tối đa, hệ số buff, nguồn tiến độ hoạt động, loại nguyên liệu hiến hợp lệ, giới hạn mỗi kỳ và phân phối Dược viên. Bonus tuân thủ trần đột phá/trọng thương đã duyệt.

Đề xuất hiến xem trước/xác nhận, không rút lại hoặc chuyển kho chung cho cá nhân. Không tự ghi nhận từ tin nhắn thô/lượt không thưởng; nếu dùng mốc sinh hoạt phải có hạn mức. Định lượng cần cân bằng để một người nhiều tài nguyên không chi phối cả nhóm.

## SECT-P03 [OPEN] Nhiệm vụ tuần và boss

Khung SECT-003. Cần chốt cách đo thành viên hoạt động, cố định mục tiêu từng kỳ, bộ nhiệm vụ, hạn mức boss, hỗ trợ được quy đổi thế nào, ngưỡng thưởng và chính sách người mới. Đề xuất chỉ hoạt động hợp lệ trong hạn mức mới tính phần thưởng kinh tế, không farm hỗ trợ vô hạn.

Cần thiết kế hợp nhất sát thương từ trận đồng thời, quyền thưởng của trận bắt đầu trước khi boss chết, cách scale độ khó/phần thưởng và thưởng mốc. Offline không đăng ký không tự bị đưa vào trận/tiêu đan.

## SECT-P04 [OPEN] Bỏ phiếu và tài nguyên chung

Luật giữ tiến trình/bỏ phiếu tại SECT-004. Cần chốt thời hạn, quorum, điều kiện bỏ phiếu, xử lý thiếu phiếu và thay ưu tiên trước khi đủ tài nguyên. Đề xuất nâng cấp/trừ quỹ nguyên tử có lịch sử, không cho cá nhân tùy ý rút tài nguyên chung.

## ECON-P01 [OPEN] Giá trị nguồn thu

Luật nguồn thu ở ECON-001. Cần chốt lượng quà nhập môn, hạn mức/linh thạch từng hoạt động và cách chống nhận lại quà theo định danh ổn định. Nguồn miễn phí phải khả thi với người mới/hết tiền, không phụ thuộc đan hồi máu bắt buộc. Phần thưởng từ nhiều hệ phải tránh tính trùng ngoài chủ đích.

## ECON-P02 [OPEN] Bảng giá và mô phỏng

Luật nguồn chi/mục tiêu ở ECON-002. Cần chốt giá từng công thức, nghi thức, roll theo cảnh giới và mô phỏng thu chi theo nhịp sinh hoạt, gồm thất bại/hoàn nguyên liệu và chữa thương. Chưa khóa giá hoặc giả định mọi ngày người chơi đều chạm trần.

## ECON-P03 [OPEN] Danh mục NPC và hạn mức

Luật cửa hàng ở ECON-003. Cần chốt hàng/giá/hạn mức/reset/quyền tặng hàng mua và xử lý tài khoản phụ. Không mở bán lại vật phẩm hoặc hộp trả tiền random khi chưa có quyết định mới. Danh mục cửa hàng phải tránh vô tình cung cấp đường mua mọi nguyên liệu đặc biệt thay cho hoạt động bắt buộc.

## ECON-P04 [OPEN] Giao dịch và phiên bản cấu hình

Luật bảo toàn tiền ở ECON-004. Cần chốt cấu trúc ledger, mã chống trùng, xác nhận lại khi giá thay đổi giữa xem và chấp nhận, hoàn lỗi hệ thống và cách phiên bản hạn mức áp dụng giữa ngày. Chưa thêm thanh toán tiền thật/đổi ra tiền thật.

## UX-P01 [OPEN] Bố cục và luồng thao tác

Điểm vào /tutien đã chốt ở UX-001. Cần thiết kế trang/nút/menu, lệnh tắt, hướng dẫn nhập môn, phân quyền thao tác và xác nhận chi phí. Không công khai số dư/túi ngoài ý muốn; khi hết phiên tương tác phải có cách mở lại bảng mới.

## UX-P02 [OPEN] Cấu hình channel

Khung ba nơi có thể gộp ở UX-002. Cần chốt mapping channel/role, quyền bot và hành vi khi channel bị xóa/thiếu quyền. Không tự tạo hàng loạt channel; cấu hình cụ thể khi triển khai trên server phải được xác định riêng.

## UX-P03 [OPEN] Thông báo chi tiết

Luật opt-in/hộp kết quả ở UX-003. Cần chốt giờ yên lặng mặc định, nhóm nhắc, lưu lịch sử bao lâu, chống gửi trùng, thông báo muộn và fallback khi không gửi được DM. Hộp kết quả lưu trong game, không phụ thuộc tuổi thọ một thông báo Discord.

## UX-P04 [OPEN] Xếp hạng và người quay lại

Khung bảng ở UX-004. Cần chốt tiêu chí, đồng hạng, ngưỡng góp hợp lệ, quyền ẩn danh/opt-out và lưu kỳ cũ. Đề xuất người quay lại thấy tóm tắt việc đã hoàn thành/mục tiêu tiếp theo, không ép bù nhiệm vụ quá hạn. Chưa thêm thưởng bù ngày nghỉ/chuỗi đăng nhập.

## BALANCE-P01 [OPEN] Áp dụng thưởng sinh hoạt

Thông số thử đã duyệt ở BALANCE-001. Còn OPEN: bộ lọc, phần lẻ, thời gian voice đi qua reset, thứ tự áp trọng thương/cap và yêu cầu đồng bộ ledger. Mô phỏng sơ bộ dùng XP tổng/ngày, chưa kiểm chứng bộ xử lý sự kiện thật.

## BALANCE-P02 [OPEN] Áp dụng hạn mức

Khung đã duyệt ở BALANCE-002. Cần chốt hoạt động đi qua reset, giữ chỗ lượt khi đang chạy và chống nhận lại/chuyển pool. Mô phỏng chưa triển khai các giao dịch đồng thời.

## BALANCE-P03 [OPEN] Bảng tiến trình và nội dung

Mục tiêu đã duyệt ở BALANCE-003. Xem balance/REPORT-EXPANDED.md cho mô hình sự kiện/auto combat/kinh tế đến Hóa Thần. Candidate-004 là bộ thử để đạt trung bình Trúc Cơ khoảng 10 ngày; chưa duyệt các công thức/drop/giá mới. Các hệ bị lược giản và giới hạn được ghi trong báo cáo.

## BALANCE-P04 [OPEN] Kiểm chứng trước triển khai

Nguyên tắc BALANCE-004. Đã mô phỏng lịch thưởng trong ngày, combat theo HP/linh lực, hỗ trợ đội mẫu, NPC, nguyên liệu sinh hoạt và bốn đại đột phá. Còn cần mở rộng thiên phú/nghề, boss đa dạng, kinh tế roll tư chất/tông môn, tác động xã hội và kiểm chứng người chơi thật trước production. Phải tách kết quả quan sát trong mô hình với dự đoán người chơi thực.
