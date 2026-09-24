# Luật đã chốt

Nguồn quyết định: hội thoại sản phẩm, tổng hợp trong [DECISIONS.md](DECISIONS.md).
Chi tiết chưa chốt nằm trong [PROPOSALS.md](PROPOSALS.md). Các luật bên dưới chưa được triển khai bởi thay đổi tài liệu này.

## CORE-001 [APPROVED] Thế giới chung

Server bạn bè hoạt động như một game tu tiên: sinh hoạt → tu vi/nguyên liệu → luyện đan → đột phá → mở hoạt động mới. Các hoạt động phải dùng chung tiến trình nhân vật thay vì những hệ điểm rời rạc.

## XP-001 [APPROVED] Nguồn tu vi

Kết hợp sinh hoạt và chơi game (lựa chọn 1B). Chat/voice cho tiến bộ đều; hoạt động game bổ sung tu vi và cung cấp nguyên liệu. Sinh hoạt trên các channel là nguồn thưởng; danh sách loại trừ và bộ lọc chi tiết chưa chốt.

## XP-002 [APPROVED] Voice hợp lệ

Lựa chọn 2B: ít nhất hai thành viên hợp lệ cùng phòng; không tính bot, AFK hoặc self-deafen. Tắt mic nhưng vẫn nghe được tính. Không ghi âm hoặc phân tích giọng nói để cấp thưởng.

## XP-003 [APPROVED] Giảm thưởng sinh hoạt

Lựa chọn 3C: chat và voice dùng chung hạn mức, nhận đầy đủ ở giai đoạn đầu, sau đó giảm thưởng và cuối cùng đạt trần. Giá trị thử nghiệm đã chốt tại BALANCE-001.

## REALM-001 [APPROVED] Cảnh giới và nhịp phát triển

Mỗi cảnh giới có 9 tầng; tầng 9 đầy tu vi là viên mãn. Phát triển ở tốc độ vừa, càng về sau càng khó; cho phép bổ sung cảnh giới sau. Mục tiêu mới Trúc Cơ trung bình khoảng 10 ngày tại BALANCE-003; các mốc sau tính lại theo độ khó tăng dần, chưa phải cam kết cho từng người.

## BREAK-001 [APPROVED] Tiểu cảnh giới

Không tự tăng tầng. Đủ tu vi và tiêu hao đan/vật phẩm phổ thông thì đột phá thành công 100%, không có thời gian chờ nghi thức. Không cần vật phẩm boss. Nguyên liệu dễ kiếm từ sinh hoạt/thám hiểm.

## BREAK-002 [APPROVED_INITIAL] Đan tăng tầng

Dùng một loại đan phổ thông trong từng cảnh giới. Các lần chuyển tầng 1→2, 2→3, 3→4: 1 viên/lần; 4→5, 5→6, 6→7: 2 viên/lần; 7→8, 8→9: 3 viên/lần. Tên Tụ Khí Đan là ví dụ cho Luyện Khí, chưa phải công thức đầy đủ.

## BREAK-003 [APPROVED] Đại cảnh giới

Cần tu vi viên mãn, đan tương ứng, linh vật đặc biệt từ boss và linh thạch; không đang trọng thương hoặc thực hiện đột phá khác. Có xác suất thất bại. Đan hỗ trợ/hộ pháp là trợ giúp tùy chọn. Nguyên liệu bắt buộc và hỗ trợ đã chọn đều tiêu hao khi thực hiện, bất kể kết quả.

Trước xác nhận phải hiển thị xác suất cuối, toàn bộ chi phí, lượng tu vi mất và thời gian trọng thương nếu thất bại.

## BOSS-001 [APPROVED] Nguồn linh vật

Boss có xác suất rơi linh vật hoàn chỉnh; mỗi lượt có thưởng hợp lệ cấp mảnh cá nhân để ghép. Không tranh phát đánh cuối; người hỗ trợ đủ điều kiện cũng nhận thưởng. Boss phải tiếp cận và đánh được ở cảnh giới trước đột phá. Linh vật khóa giao dịch ở bản đầu.

## BOSS-002 [APPROVED_INITIAL] Bảo đảm nguyên liệu

Ví dụ khởi đầu: tối đa 5 lượt boss có thưởng đủ mảnh ghép một linh vật nếu chưa rơi nguyên món. Điều kiện đóng góp, giới hạn lượt có thưởng và xác suất rơi cần thiết kế ở module boss.

## FAIL-001 [APPROVED_INITIAL] Mất tu vi mức nhẹ

Thất bại mất 10% lượng tu vi cần lấp đầy tầng 9 hiện tại, không phải 10% tổng tu vi trọn đời. Giữ nguyên tầng và đại cảnh giới. Ví dụ thanh 1.000/1.000 còn 900/1.000. Tu vi dự trữ nếu có không bù ngay khoản phạt; chỉ mở sau thành công. Chưa chốt có bể dự trữ hay không và kích thước bể.

## INJURY-001 [APPROVED] Trọng thương

Không đột phá khi trọng thương. Vẫn chat, voice, luyện đan, thám hiểm và tham gia phó bản. Hồi phục tính theo thời gian thực kể cả offline. Không làm giảm máu tối đa khiến nhân vật chết ngay khi nhận trạng thái.

## INJURY-002 [APPROVED_INITIAL] Mức phạt và hồi phục

Tu vi thực nhận từ mọi nguồn giảm 50%; phần thực nhận mới tính vào hạn mức. Hiệu quả chiến đấu giảm 20% (cách áp dụng trong công thức còn OPEN). Thất bại lên Trúc Cơ: 6 giờ; Kim Đan: 12 giờ; cảnh giới sau tăng nhưng ban đầu tối đa 24 giờ. Thuốc giảm tối đa 50% tổng thời gian của mỗi lần trọng thương.

## INSIGHT-001 [APPROVED] Cảm ngộ

Gắn với cửa ải đại cảnh giới đang thử; tăng xác suất sau thất bại, không hết hạn khi nghỉ chơi, không phải tiền. Xóa cảm ngộ của cửa ải khi thành công. Có ngưỡng bảo đảm thành công; hỗ trợ có thể đưa xác suất lên 100% sớm hơn.

## INSIGHT-002 [APPROVED_INITIAL] Ví dụ Trúc Cơ

Cơ bản 50%, mỗi thất bại cộng 15 điểm phần trăm, tối đa 100%: 50 → 65 → 80 → 95 → 100. Các cảnh giới sau cần cấu hình riêng; không mặc định tăng đồng thời mọi hình phạt.

## CHAR-001 [APPROVED] Hồ sơ

Tự tạo hồ sơ ở hoạt động hợp lệ đầu tiên và nhận tu vi ngay. Đạo danh mặc định từ tên hiển thị; chọn lại khi mở hồ sơ lần đầu. Không tự đổi nickname Discord. Có lựa chọn ngừng tham gia, dừng nhận thưởng và thông báo cá nhân.

Công khai cảnh giới, hướng tu luyện, danh hiệu và thành tích; túi đồ chi tiết, số dư và tiến độ chuẩn bị đột phá mặc định riêng tư.

## CHAR-002 [APPROVED] Thuộc tính

Bốn thuộc tính cốt lõi: sinh lực, công kích, phòng ngự, linh lực. Tự tăng theo tầng/cảnh giới, chưa cộng điểm thủ công. Tu vi là kinh nghiệm; linh lực dùng kỹ năng trong trận và hồi khi bắt đầu hoạt động mới; linh thạch là tiền. Nếu có thể lực thám hiểm phải là tài nguyên riêng.

Giá trị khởi đầu của bốn thuộc tính được roll cùng bộ tư chất (GEN-001); tăng trưởng do tầng/cảnh giới là lớp riêng. Hai chỉ số duyên/nạn là Phúc duyên và Kiếp số (GEN-004); phân phối và công thức còn OPEN (GEN-P02).

## CHAR-003 [APPROVED] Hướng tu luyện và nghề

Mở ở Trúc Cơ: Kiếm tu (tấn công), Thể tu (bảo vệ), Pháp tu (hỗ trợ/khống chế). Mỗi hướng có một nội tại và khoảng hai kỹ năng ở bản đầu; kỹ năng được hệ thống tự sử dụng trong auto combat, không yêu cầu bấm theo lượt (COMBAT-001). Các hướng đều có khả năng chơi cá nhân; phó bản cơ bản không bắt buộc đủ ba hướng. Luyện đan và các nghề tương lai tách riêng, không bị khóa theo hướng.

## CHAR-004 [APPROVED] Đổi hướng

Chọn lần đầu miễn phí, một lần đổi miễn phí sau khi thử. Các lần sau dùng vật phẩm phổ thông và thời gian chờ chưa chốt. Không đổi khi đang phó bản/chiến đấu. Giữ cảnh giới, tu vi, nghề và túi đồ. Đổi hướng tu luyện khác với roll tư chất; roll sau mốc đầu tuân theo GEN-002, không mặc định hưởng lần đổi hướng miễn phí.

## CHAR-005 [APPROVED] Role và danh hiệu

Bot quản lý một role cảnh giới hiện tại mỗi người. Tầng nhỏ nằm trong hồ sơ. Danh hiệu từ thành tích, chọn một để hiển thị; chưa cộng sức mạnh ở bản đầu. Không tạo role cho mỗi tầng/danh hiệu.

## GEN-001 [APPROVED] Thiên phú và linh căn ngẫu nhiên

Một bộ gồm một linh căn và hai thiên phú ngẫu nhiên, cùng chỉ số khởi đầu và chỉ số ảnh hưởng xác suất duyên/nạn. Roll cả bộ, được xem bộ mới và giữ bộ cũ; không ghép thuộc tính từ nhiều bộ. Yêu cầu này thay thế linh căn tự chọn/chỉ mang tính cá tính trước đó. Phân phối, độ hiếm, hiệu ứng và dải chỉ số chưa chốt; xem GEN-P01–03.

## GEN-002 [APPROVED] Giai đoạn roll miễn phí và trả giá

Roll khởi đầu miễn phí vô hạn trước lần đột phá tiểu cảnh giới đầu tiên. Sau mốc đó vẫn được roll lại nhưng phải trả giá (GEN-005). Không dùng đề xuất giới hạn 10 lượt hoặc 3 lượt/ngày. Mốc triển khai đề xuất Luyện Khí 1→2 vẫn cần làm rõ cùng bước nhập môn (GEN-P01).

## GEN-003 [APPROVED] Ngân sách chỉ số chiến đấu

Bốn chỉ số khởi đầu roll theo ngân sách cân bằng, chỉ số cao đánh đổi chỉ số khác. Dùng tỉ lệ chuẩn hóa, không cộng thẳng các đại lượng khác đơn vị. Không roll độc lập để có bộ vượt trội toàn diện. Dải 90–110% từng chỉ số là ví dụ khởi đầu, chưa khóa dải hoặc thuật toán lấy mẫu.

## GEN-004 [APPROVED] Phúc duyên và Kiếp số

Phúc duyên ảnh hưởng cơ hội kỳ ngộ; Kiếp số ảnh hưởng khả năng gặp hoặc tốc độ tích lũy áp lực kiếp nạn. Có thể có bộ nhiều cơ duyên nhưng cũng nhiều tai kiếp. Thiên phú mạnh có thể kèm Kiếp số cao, công khai trong tư chất. Không chỉ số nào loại bỏ hoàn toàn duyên hoặc nạn.

Chưa cho hai chỉ số tác động trực tiếp đến chí mạng, rơi đồ boss hoặc đại đột phá. Kiếp số không vô hiệu hóa bảo đảm cảm ngộ. Việc công khai tư chất không tiết lộ kết quả một lựa chọn sự kiện cụ thể (EVENT-002).

## GEN-005 [APPROVED] Giá roll sau mốc miễn phí

Tiêu hao Tẩy Tủy Đan và linh thạch khi sinh bộ mới. Xem chi phí và xác nhận trước khi trả; sau khi xem kết quả có thể nhận bộ mới hoặc giữ bộ cũ, giữ cũ vẫn mất phí. Giá tăng theo đại cảnh giới, không tăng vô hạn theo số lần roll trọn đời. Nguồn đan, giá cụ thể và cooldown còn OPEN.

## GEN-006 [APPROVED] Bảo toàn tiến trình khi roll

Chỉ đổi tư chất gốc rồi tính lại chỉ số hiện tại; giữ cảnh giới/tầng, tu vi, hướng tu luyện, nghề, trang bị, túi đồ, cảm ngộ, trọng thương, áp lực kiếp nạn và tiến trình sự kiện. Không hồi đầy máu hoặc xóa trọng thương bằng roll. Không roll giữa combat, phó bản hay đột phá. Các quy tắc kỹ thuật chi tiết còn trong GEN-P03.

## COMBAT-001 [APPROVED] Auto combat cho cá nhân và tổ đội

Thay thế toàn bộ mô hình turn-based yêu cầu người chơi chọn hành động mỗi vòng. Người chơi thao tác chuẩn bị/khởi động, hệ thống tự chạy quá trình chiến đấu có diễn biến và biến số, sau một khoảng thời gian kết thúc. Áp dụng thống nhất cho săn quái, phó bản, boss, combat sự kiện/kiếp nạn, cả cá nhân lẫn tổ đội.

Giữ vai trò thuộc tính, hướng tu luyện và ngẫu nhiên. Không yêu cầu bấm đánh, dùng kỹ năng, phòng thủ hoặc xác nhận liên tục trong trận. Không chuyển yêu cầu thao tác từng lượt sang trưởng đội. Chuẩn bị, diễn biến và thời lượng theo COMBAT-002–005; công thức và chi tiết kỹ thuật còn OPEN tại COMBAT-P01/02.

## COMBAT-002 [APPROVED] Chiến thuật và ngân sách đan

Ba chiến thuật lưu làm mặc định: Công kích, Cân bằng, Thận trọng. Chọn mục tiêu, dùng cấu hình đã lưu và xuất chiến; không cần thiết lập lại mỗi trận. Cho tự dùng đan trong ngân sách người chơi đã xác nhận; mặc định không dùng nếu chưa cho phép. Không lấy thêm từ túi ngoài ngân sách; đan chưa dùng trả lại. Số viên và ngưỡng máu cụ thể còn OPEN, ví dụ hai viên/dưới 30% chưa khóa.

## COMBAT-003 [APPROVED] Sẵn sàng tổ đội

Chủ đội chọn phó bản; mỗi người tham gia và xác nhận chiến thuật/ngân sách cá nhân một lần. Tất cả sẵn sàng thì xuất phát, không cần trưởng đội điều khiển từng người. Trưởng đội không có quyền tăng tiêu hao của người khác. Offline sau bắt đầu không tước thưởng: nhân vật vẫn tự chiến đấu, đóng góp gồm sát thương/bảo vệ/hỗ trợ.

## COMBAT-004 [APPROVED] Diễn biến và báo cáo

Mô phỏng chiến đấu thực theo nhiều nhịp tự động: dùng kỹ năng/linh lực, chí mạng, dao động sát thương, kháng hiệu ứng, phối hợp vai trò và hành vi boss. Thuộc tính, chiến thuật và phối hợp tác động đến kết quả. Nhật ký từ cùng mô phỏng, không tung một lần thắng/thua rồi tạo diễn biến minh họa độc lập.

Chạy khi người dùng offline; cập nhật một thông báo tiến trình ở vài mốc quan trọng và tổng kết khi xong, không spam từng đòn hoặc yêu cầu theo dõi màn hình.

## COMBAT-005 [APPROVED_INITIAL] Thời lượng thử nghiệm

Quái thường 30–60 giây; tinh anh/boss cá nhân 1–3 phút; toàn phó bản 3–5 phút không tính chờ lập đội. Đây là khung thử nghiệm có thể cân bằng lại; cần thiết kế số nhịp, sức mạnh và chờ sự kiện để tổng thời gian phù hợp. Chưa chốt xử lý bế tắc/hòa/giới hạn thời gian cứng.

## EVENT-001 [APPROVED] Kỳ ngộ và kiếp nạn

Bổ sung cả kỳ ngộ và kiếp nạn để cân bằng tiến trình; kết quả gắn với lựa chọn theo EVENT-002–005. Đã chốt giới hạn hậu quả sự kiện thường; chưa chốt điều kiện kích hoạt, giá trị thưởng/phạt, tần suất và công thức liên hệ với tư chất; xem EVENT-P01–03.

## EVENT-002 [APPROVED] Duyên/nạn ẩn sau lựa chọn

Cơ duyên hoặc kiếp nạn được ẩn sau lựa chọn của người dùng; chọn rồi mới biết kết quả. Có gợi ý bằng cốt truyện, không hiện loại kết quả hoặc xác suất từng nhánh trước chọn. Không gắn nhãn trước rằng một nút chắc chắn dẫn tới kỳ ngộ hay kiếp nạn. Không suy diễn thành ẩn chỉ số tư chất trên hồ sơ hoặc sửa luật công khai xác suất/chi phí đại đột phá (BREAK-003).

## EVENT-003 [APPROVED] Lựa chọn và kết quả ngẫu nhiên

Cùng một lựa chọn có thể dẫn đến kết quả khác nhau giữa những lần gặp. Mỗi lựa chọn có nhóm kết quả và xác suất riêng, chịu ảnh hưởng Phúc duyên/Kiếp số; hành động được chọn phải ảnh hưởng thực sự đến kết quả. Kết quả đã xác định được lưu, bấm lại hoặc reconnect không đổi kết quả. Công thức, bảng xác suất và thời điểm chụp trạng thái tư chất chưa chốt.

## EVENT-004 [APPROVED] Rời đi và bỏ lỡ

Có lựa chọn rời đi, không thưởng và không phạt. Sự kiện hết hạn khi chưa chọn cũng kết thúc không thưởng/không phạt. Chưa chốt thời hạn. Quy tắc này không có nghĩa được hủy một kết quả đã chọn để né hậu quả.

## EVENT-005 [APPROVED] Giới hạn hậu quả sự kiện

Sự kiện thường có thể cấp nguyên liệu, linh thạch, mảnh công thức, hỗ trợ tạm thời hoặc nhiệm vụ; hậu quả bất lợi có thể là tiêu hao vật tư, suy yếu tạm thời hoặc mở trận chiến. Không mất tu vi, không tụt tầng/cảnh giới, không mất vĩnh viễn trang bị do sự kiện thường. Giá trị thưởng, lượng vật tư tiêu hao và thời gian suy yếu chưa chốt.

Kiếp nạn lớn có bước xử lý tiếp, ví dụ đương đầu, tìm trợ giúp hoặc trả giá để thoát; lựa chọn cụ thể và mức giá/hậu quả còn cần thiết kế. Không tự áp hình phạt đột phá lên sự kiện hoặc phê duyệt mọi hình phạt cho kiếp nạn lớn. Luật FAIL-001 của đại đột phá không đổi.

## ITEM-001 [APPROVED] Túi đồ

Bản đầu không giới hạn ô nguyên liệu/đan; vật phẩm giống nhau xếp chồng và không tự hết hạn. Linh thạch là số dư riêng. Túi chi tiết riêng tư, có lọc/tìm kiếm. Hiển thị số lượng, công dụng, nguồn kiếm và quyền chuyển giao; không tự bán/hủy đồ. Đồ khác phẩm cấp hoặc trạng thái khóa không xếp chung.

## ITEM-002 [APPROVED] Phân nhóm và công thức

Năm nhóm: nguyên liệu, đan dược, linh vật/mảnh boss, công thức/mảnh công thức, vật phẩm sự kiện/nhiệm vụ. Công thức học một lần dùng lâu dài, không mất sau mỗi mẻ luyện. Hệ trang bị chưa nằm trong phạm vi thiết kế này.

## ITEM-003 [APPROVED_INITIAL] Danh mục nguyên liệu khởi đầu

Bắt đầu với nguyên liệu sơ cấp: Linh thảo cho đan phổ thông; Linh hoa cho đan hỗ trợ; Yêu huyết cho đan hồi phục; Yêu đan cho công thức cao hơn; Linh tuyền làm dung môi; Tẩy tủy thảo cho Tẩy Tủy Đan. Đây là danh mục ban đầu, có thể điều chỉnh khi chốt công thức. Chưa tạo hàng loạt biến thể phẩm cấp. Linh vật boss đại đột phá riêng biệt, không thay bằng Yêu đan thường.

## ITEM-004 [APPROVED] Nguồn nguyên liệu

Chat/voice cấp nguyên liệu phổ thông qua mốc hoạt động giới hạn, không drop từng tin nhắn. Thám hiểm chọn địa điểm để tìm nhóm nguyên liệu; quái/phó bản cung cấp nguyên liệu chiến đấu/chế tạo; boss theo BOSS-001/002. Kỳ ngộ là nguồn bổ sung, không là nguồn duy nhất cho nguyên liệu bắt buộc.

Mỗi nguyên liệu bắt buộc để tăng tầng có ít nhất một nguồn chủ động, đáng tin cậy; Tẩy tủy thảo cũng không chỉ từ kỳ ngộ hiếm. Tỉ lệ rơi, hạn mức và sản lượng chưa chốt.

## ITEM-005 [APPROVED] Tặng đồ và khóa chuyển giao

Bản đầu cho tặng nguyên liệu thường và đan phổ thông. Linh vật/mảnh boss, vật phẩm nhiệm vụ và Tẩy Tủy Đan khóa chuyển giao. Chưa mở chợ, đấu giá hoặc chuyển linh thạch. Không dùng thành phần khóa để tạo sản phẩm tự do chuyển giao nhằm né khóa. Danh sách SKU được tặng, quy tắc kế thừa khóa và giới hạn tặng cần đặc tả thêm; không mặc định mọi đan đều là đan phổ thông.

## ALCHEMY-001 [APPROVED] Nhập môn và công thức

Mọi hướng học luyện đan từ Luyện Khí tầng 1. Cấp nghề riêng: Đan đồ → Đan sư sơ cấp → Trung cấp → Cao cấp; mốc XP chưa chốt. Nhập môn có công thức đan tăng tầng và hồi phục. Công thức bắt buộc có đường mở chủ động ở cảnh giới trước cửa ải cần nó; kỳ ngộ có thể mở sớm hoặc thêm công thức đặc biệt.

## ALCHEMY-002 [APPROVED_INITIAL] Sáu loại đan đầu tiên

Tụ Khí Đan để tăng tầng nhỏ; Hồi Xuân Đan hồi máu combat; Dưỡng Thương Đan rút thời gian trọng thương; Hộ Mạch Đan hỗ trợ xác suất đột phá; Trúc Cơ Đan dùng lên Trúc Cơ; Tẩy Tủy Đan đổi tư chất. Công thức/hiệu lực cụ thể còn OPEN. Linh vật boss chỉ tiêu hao ở nghi thức đại đột phá, không tiêu hao thêm khi luyện Trúc Cơ Đan.

## ALCHEMY-003 [APPROVED] Mẻ luyện

Một lò hoạt động mỗi nhân vật, chọn công thức và số lượng; hiển thị tổng chi phí, thời gian, xác suất trước xác nhận. Trừ nguyên liệu/linh thạch khi bắt đầu. Luyện tiếp khi offline, hoàn tất tự vào túi, không hỏng do quên nhận; có thể sinh hoạt/thám hiểm trong lúc chờ. Cấp nghề và thiên phú áp dụng theo lúc bắt đầu, roll tư chất sau đó không đổi mẻ. Giới hạn mẻ và thời gian cụ thể chưa chốt.

## ALCHEMY-004 [APPROVED] Thành công và thất bại phương án B

Đan phổ thông/tăng tầng thành công 100%. Đan đặc biệt như Trúc Cơ Đan và Tẩy Tủy Đan có thể thất bại, xác suất được xem trước. Phân loại Hộ Mạch Đan và xác suất nền còn OPEN.

Thất bại từng viên hoàn 50% số lượng mỗi nguyên liệu đã tiêu hao, làm tròn xuống; phí linh thạch không hoàn. Hiển thị chính xác lượng hoàn trước luyện. Không mất tu vi hoặc gây trọng thương. Sau hai thất bại liên tiếp cùng công thức, viên tiếp theo bảo đảm thành công. Thành công reset chuỗi công thức; mẻ nhiều viên xử lý lần lượt. Bộ đếm không mất khi offline hoặc roll tư chất.

## ALCHEMY-005 [APPROVED] Chất lượng và cấp nghề

Hai chất lượng: đạt chuẩn dùng đủ công dụng và thượng phẩm có hiệu quả tốt hơn theo từng loại. Riêng đan tăng tầng nhỏ/Tẩy Tủy Đan bản đầu chỉ một chất lượng. Chất lượng không bỏ khóa chuyển giao hoặc vượt trần xác suất đột phá/giảm thời gian trọng thương đã duyệt.

Cấp nghề mở công thức, cải thiện chất lượng hoặc xác suất thành công. Công thức quá thấp cấp cho XP nghề giảm dần. XP, hệ số chất lượng và bảng tỉ lệ chưa chốt; không mặc định Phúc duyên/Kiếp số ảnh hưởng luyện đan.

## ACTIVITY-001 [APPROVED] Thám hiểm

Một chuyến đang chạy mỗi nhân vật; chọn địa điểm theo nguồn nguyên liệu và xem thời gian/phần thưởng trước khi đi. Tiếp tục offline, hoàn tất tự vào túi. Mỗi chuyến bảo đảm lượng nguyên liệu mục tiêu cơ bản, phần thêm ngẫu nhiên. Có thể phát sinh sự kiện lựa chọn ẩn; bỏ lỡ sự kiện không mất thưởng cơ bản. Vẫn chat/voice/luyện đan trong lúc chờ. Thời gian và sản lượng cụ thể chưa chốt.

## ACTIVITY-002 [APPROVED] Săn quái

Chọn khu vực và đối thủ; quái thường cho nguyên liệu ổn định, tinh anh khó hơn/thưởng tốt hơn. Hiển thị độ khó tương đối và nhóm nguyên liệu trước trận. Một trận đang diễn ra mỗi người. Luyện Khí có kỹ năng nhập môn chung trước khi chọn hướng ở Trúc Cơ. Combat tự động theo COMBAT-001, thay phần săn quái theo lượt trong đề xuất cũ.

## ACTIVITY-003 [APPROVED] Phó bản và boss cá nhân

Đội 2–4 người tham gia/sẵn sàng bằng nút; bản đầu gồm ba chặng: quái → sự kiện lựa chọn → boss. Độ khó theo số người và bậc phó bản, không bắt đủ ba hướng. Phần thưởng riêng mỗi người; đóng góp bảo vệ/hỗ trợ đều được tính. Có phó bản nhập môn Luyện Khí và thử thách boss cá nhân kiếm vật liệu đại đột phá khi không đủ đội. Linh vật/mảnh theo BOSS-001/002. Boss toàn server để mở rộng, không là cửa chặn vật liệu bắt buộc.

Các chặng combat chạy tự động cho toàn đội. Sự kiện lựa chọn ẩn vẫn tồn tại theo ACTIVITY-005; thời hạn cụ thể còn OPEN.

## ACTIVITY-004 [APPROVED] Hạn mức và thất bại

Dùng hạn mức lượt nhận thưởng riêng từng hoạt động mỗi ngày, chưa thêm thể lực chung. Hết lượt vẫn được giúp bạn/luyện chiến thuật nhưng không nhận thêm tu vi, vật phẩm hoặc mảnh boss; báo rõ trước khi vào. Hạn mức chat/voice vẫn riêng theo XP-003. Số lượt và reset chưa chốt.

Thua giữ thưởng chặng đã xong, không nhận thưởng chặng chưa vượt; vật phẩm đã dùng không hoàn. Không mất tu vi hiện có, không rơi trang bị, không tự áp trọng thương đột phá cho combat. Lượt thưởng trừ khi nhận thưởng chặng đầu: thua trước đó không trừ, đã nhận thưởng không hoàn lượt. Chi tiết chống farm/bấm lặp và khôi phục lỗi hệ thống còn OPEN.

## ACTIVITY-005 [APPROVED] Sự kiện trong phó bản auto

Tối đa một điểm lựa chọn sự kiện trong chuyến phó bản bản đầu, một đại diện chọn thay đội. Không chọn trong thời hạn ngắn thì bỏ qua an toàn và tiếp tục; đội offline vẫn hoàn thành được chuyến. Không tự tiêu thêm vật phẩm cá nhân ngoài mức đã đồng thuận. Cách chỉ định đại diện, thời hạn và xử lý người đại diện rời đội chưa chốt.

## SECT-001 [APPROVED] Một tông môn chung

Bản đầu cả server là một tông môn, mọi nhân vật tham gia thuộc tông môn này. Chủ server đặt tên, mô tả và biểu tượng. Chưa chia nhiều phe cạnh tranh. Chức danh game không tự cấp quyền quản trị Discord.

## SECT-002 [APPROVED] Công trình và đóng góp

Bốn công trình ban đầu: Đan phòng hỗ trợ luyện đan; Dược viên cung cấp nguyên liệu phổ thông; Tàng Kinh Các mở nội dung/công thức bổ sung; Hộ Sơn Đại Trận hỗ trợ phòng thủ và boss tông môn. Không khóa công thức/nguyên liệu bắt buộc để cá nhân đột phá sau cấp công trình.

Nâng cấp bằng hoạt động hợp lệ của thành viên và hiến nguyên liệu tự nguyện; không tự lấy từ túi. Giới hạn phần hiến được tính mỗi người theo kỳ. Điểm cống hiến là thành tích, chưa là tiền để tiêu. Hệ số, giới hạn, hiệu lực và cách phân phối sản phẩm công trình còn OPEN.

## SECT-003 [APPROVED] Nhiệm vụ tuần và boss bất đồng bộ

Nhiệm vụ tuần có nhiều cách góp sức qua thám hiểm, luyện đan, phó bản và hỗ trợ; mục tiêu theo lượng thành viên thực sự tham gia game. Boss tồn tại trong khoảng sự kiện, mỗi người/đội chủ động chọn lúc đánh auto, kết quả góp vào tiến độ chung. Có hạn mức lượt thưởng; ghi nhận tham gia/hỗ trợ thay vì chỉ top sát thương. Boss không độc quyền vật liệu đột phá. Điều kiện nhận thưởng chung và cách đo lượng thành viên hoạt động chưa chốt.

## SECT-004 [APPROVED] Quản lý nâng cấp và giữ tiến trình

Thành viên bỏ phiếu công trình ưu tiên, hòa thì chủ server quyết định. Đủ tài nguyên mới nâng, đóng góp và sử dụng có lịch sử. Công trình không tụt cấp khi nghỉ; nhiệm vụ tuần reset nhưng thành tích/cảnh giới giữ nguyên. Boss thất bại không phá công trình hoặc lấy đồ cá nhân; tài nguyên chung chưa dùng được giữ. Thời hạn phiếu, quorum và cách xử lý thiếu phiếu còn OPEN.

## ECON-001 [APPROVED] Tiền và nguồn thu

Bản đầu chỉ có linh thạch làm tiền; tu vi/cống hiến không đổi thành tiền. Kiếm qua thám hiểm, săn quái, phó bản, nhiệm vụ tông môn và kỳ ngộ theo hạn mức. Chat/voice chủ yếu cho tu vi/nguyên liệu, không trả linh thạch từng tin nhắn.

Quà nhập môn một lần đủ thử vài mẻ đan; không cấp lại khi roll hoặc rời/vào server. Luôn có nguồn kiếm tiền cơ bản không thu phí vào cửa để người hết tiền vẫn tự kiếm lại được. Giá trị quà và nguồn thu cụ thể chưa chốt.

## ECON-002 [APPROVED] Nơi tiêu và mục tiêu cân bằng

Linh thạch dùng phí luyện đan, đại đột phá, roll tư chất trả phí và mua nguyên liệu thường ở NPC. Không có phí bảo trì nhân vật/công trình. Mục tiêu nhịp vừa đủ luyện đan tiến trình và tích lũy cho đột phá; roll trả phí cần dành dụm thêm. Cần tính nguồn thu và chi phí thất bại trước khi khóa giá.

## ECON-003 [APPROVED] Cửa hàng NPC

Bán nguyên liệu phổ thông theo hạn mức riêng từng người mỗi ngày. Không bán linh vật/mảnh boss, đan đại đột phá, Tẩy Tủy Đan hoặc vật phẩm bỏ qua cửa ải. Chưa cho bán đồ lấy linh thạch. Đồ dư dùng luyện/tặng/hiến theo quyền đã chốt. Cửa hàng NPC không thay đổi luật chưa mở chợ người chơi, đấu giá và chuyển linh thạch. Danh mục, giá và hạn mức chưa chốt.

## ECON-004 [APPROVED] Bảo toàn tiền và giá

Không reset tiền khi nghỉ, không âm số dư hoặc vay nợ. Hiển thị giá trước xác nhận, có lịch sử nguồn thu/chi. Thiếu tiền không trừ dở nguyên liệu; restart/bấm trùng không trừ hoặc phát hai lần. Giá mới chỉ áp dụng thao tác chưa xác nhận; hoạt động/mẻ đang chạy giữ giá đã chấp nhận. Cách triển khai sổ giao dịch và phiên bản cấu hình còn OPEN.

## UX-001 [APPROVED] Bảng cá nhân

/tutien là điểm vào chính, hiển thị cảnh giới/tu vi/linh thạch/trạng thái, tác vụ đang chạy và việc làm tiếp. Nút/menu mở túi, luyện đan, hoạt động, đột phá và tông môn. Chỉ rõ điều kiện còn thiếu, nguyên liệu và nguồn kiếm. Chiến thuật lưu sẵn, ít thao tác. Số dư/túi riêng tư theo CHAR-001.

## UX-002 [APPROVED] Không gian game

Ba nơi cấu hình: khu chơi bot, thành tựu, tông môn; có thể gộp theo server. Chat/voice ở channel hợp lệ khác vẫn nhận tu vi. Đại đột phá/thành tích hiếm/mốc chung có thể thông báo công khai; tăng tầng nhỏ/thu nhập thường vào kết quả cá nhân.

## UX-003 [APPROVED] Hộp kết quả và nhắc tự đăng ký

Mặc định ít thông báo, không DM hoặc ping mọi người cho từng tác vụ, không thông báo mỗi lần nhận XP. Tác vụ hoàn tất tự trả thưởng và lưu kết quả cá nhân; nhắc luyện đan/thám hiểm/boss/kèo đội do người chơi tự bật, có giờ yên lặng/tắt nhắc. Trận đội cập nhật ở thông báo chung. Offline hoặc không gửi được tin không làm mất thưởng; không yêu cầu mở tin để nhận kết quả.

## UX-004 [APPROVED] Bảng xếp hạng

Ba bảng đầu: cảnh giới lâu dài, cống hiến tông môn tuần, thành tích hoạt động tuần có ghi nhận hỗ trợ thay vì chỉ sát thương. Không xếp hạng số tin nhắn/thời gian treo voice. Reset điểm kỳ tuần không reset nhân vật hoặc thành tích đã đạt. Chỉ ghi nhận/danh hiệu, chưa thưởng sức mạnh cho top. Tiêu chí chi tiết, đồng hạng và giờ reset chưa chốt.

## BALANCE-001 [APPROVED_INITIAL] Tu vi sinh hoạt

Chat hợp lệ 10 tu vi, tối đa một lần mỗi 60 giây/người toàn server; voice hợp lệ 20 tu vi/5 phút. Hai nguồn cộng đồng thời, chung hạn mức: 600 đầu ngày đủ mức, sau đó 25% mức gốc, tối đa 900 tu vi sinh hoạt/ngày. Tu vi game ngoài trần sinh hoạt, chịu giới hạn thưởng riêng. Reset 04:00 Asia/Ho_Chi_Minh. Bộ lọc/phần lẻ và thứ tự áp trọng thương còn cần đặc tả.

## BALANCE-002 [APPROVED_INITIAL] Hạn mức hoạt động

Mỗi ngày 3 chuyến thám hiểm (20 phút/chuyến), 5 trận săn quái, 2 lượt chung phó bản/boss cá nhân. Boss tông môn 2 lượt mỗi đợt sự kiện riêng. Ngày reset 04:00, tuần 04:00 thứ Hai, Asia/Ho_Chi_Minh. Chưa cộng dồn lượt bỏ lỡ, không tự lặp hoạt động. Đây là trần tùy chọn, không yêu cầu hoàn thành hết. Cách trừ lượt theo ACTIVITY-004.

## BALANCE-003 [APPROVED_INITIAL] Mốc nhập môn và mục tiêu tiến trình

Phàm Nhân → Luyện Khí là nhập môn trong buổi đầu, Luyện Khí tầng 1 → tầng 2 kết thúc roll miễn phí vô hạn. Mục tiêu người chơi vừa sinh hoạt 4–5 ngày/tuần đạt Trúc Cơ trung bình khoảng 10 ngày tính từ đầu; gồm vật liệu, luyện, thất bại và hồi phục. Các mốc Kim Đan và cảnh giới sau tính lại từ nhịp mới và scale khó dần; mốc cũ 6–8 tuần không còn ràng buộc cố định. Đây là mục tiêu cần kiểm chứng, không bảo đảm cho từng người.

## BALANCE-004 [APPROVED] Cân bằng qua mô phỏng

Xây bảng giá/công thức/phần thưởng/tu vi cùng nhau, mô phỏng người ít/vừa/nhiều chơi, đưa lại kết quả và các điểm cần điều chỉnh. Thông số thử có thể điều chỉnh; không tự thay luật, reset nhân vật, tịch thu đồ hay hạ cảnh giới đã đạt. Giá đã chấp nhận theo ECON-004. Cấu hình candidate của mô phỏng không tự trở thành cấu hình được duyệt.

## DOC-001 [APPROVED] Tài liệu trong repo

Toàn bộ tài liệu cơ chế phải đồng bộ trong repo để trích xuất và so sánh bất kỳ lúc nào. Duy trì luật hiện hành, đề xuất chưa duyệt và lịch sử thay đổi, tham chiếu bằng mã ổn định.
