# Thiết kế game tu tiên Virtus

Phiên bản thiết kế: `0.14.0` · Ngày đồng bộ: 2026-09-24. Thay đổi mới nhất: D030–D031 (mục tiêu Trúc Cơ khoảng 10 ngày; mô phỏng auto combat, vật liệu, NPC và bốn mốc cảnh giới).

- [IMPLEMENTATION.md](IMPLEMENTATION.md): trạng thái runtime 1.0 thực tế, tự setup Discord, giới hạn và cách chạy kiểm thử.

## Nguồn chuẩn

- [RULES.md](RULES.md): cơ chế đã chốt, mã luật ổn định và cấu hình ban đầu được duyệt.
- [PROPOSALS.md](PROPOSALS.md): phương án chưa duyệt, thông số chưa khóa và câu hỏi cần giải quyết.
- [DECISIONS.md](DECISIONS.md): lịch sử quyết định, bằng chứng hội thoại và các phương án bị thay thế.

Đây là tài liệu sản phẩm, chưa phải bằng chứng triển khai hoặc kiểm thử game. Không tự coi phần mềm hiện tại đã tuân thủ các luật này.

- [balance/REPORT-EXPANDED.md](balance/REPORT-EXPANDED.md): kết quả mô phỏng hiện hành, công thức, giả định và giới hạn.
- [balance/REPORT.md](balance/REPORT.md): báo cáo sơ bộ cũ, giữ để so sánh; không dùng làm mục tiêu hiện hành.

## Quy ước đồng bộ

1. Sau mỗi lần người dùng chốt, cập nhật luật tương ứng trong RULES, trạng thái đề xuất trong PROPOSALS và thêm lịch sử vào DECISIONS trong cùng thay đổi.
2. Dùng mã luật ổn định để tìm, trích xuất và đối chiếu. Không tái sử dụng mã cho một ý nghĩa khác.
3. Mỗi cơ chế chỉ có một mô tả chuẩn. Tài liệu khác tham chiếu mã thay vì sao chép thông số.
4. Phân biệt `APPROVED` (luật), `APPROVED_INITIAL` (cấu hình khởi đầu được duyệt, có thể cân bằng lại), `PROPOSED` (chưa duyệt), `OPEN` (thiếu quyết định), `SUPERSEDED` (đã thay thế).
5. Phê duyệt khái niệm không đồng nghĩa phê duyệt xác suất, công thức hoặc giới hạn chưa được nêu. Mọi chỉnh sửa thông số đã duyệt phải có mục lịch sử mới.
6. Khi một đề xuất được thay thế, ghi lý do trong DECISIONS; không âm thầm xóa dấu vết quyết định.
7. Mọi thay đổi cơ chế tiếp theo phải đi kèm cập nhật bộ tài liệu này. Không dùng riêng nội dung hội thoại làm đặc tả triển khai.

## Trích xuất và so sánh

Các file Markdown UTF-8 có thể đọc hoặc xuất trực tiếp, không phụ thuộc công cụ bên ngoài.

```sh
# Liệt kê toàn bộ mã luật và trạng thái.
rg '^## ' docs/game/RULES.md docs/game/PROPOSALS.md
# Đọc một luật (ví dụ CORE-001) cùng nội dung đến luật kế tiếp.
sed -n '/^## CORE-001 /,/^## /p' docs/game/RULES.md
# Xem thay đổi đang chuẩn bị, và lịch sử sau khi tài liệu được commit.
git diff -- docs/game README.md
git log -p -- docs/game
# So sánh hai revision đã chứa tài liệu; thay REV_A và REV_B bằng ref thật.
git diff REV_A REV_B -- docs/game
```

Lưu ý: file mới chưa được Git theo dõi không xuất hiện trong `git diff`; dùng `git status --short` để phát hiện. Lịch sử liên phiên bản chỉ có sau khi các phiên bản được commit. Phiên đồng bộ đầu tiên không tự commit hoặc push.

## Các phần chưa thiết kế đầy đủ

Hệ vật phẩm/túi đồ; công thức luyện đan; thám hiểm; phó bản/boss; kinh tế/giao dịch; tông môn; quản trị; triển khai kỹ thuật. Những tên vật phẩm xuất hiện trong ví dụ chưa phải danh mục nội dung hoàn chỉnh.

- [RELEASE.md](RELEASE.md): phiên bản phát hành, kiểm thử, migration và bằng chứng rollout.
