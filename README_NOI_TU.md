# Trò Chơi Nối Từ - Discord Bot

## Mô tả
Trò chơi nối từ là một mini-game trong Discord bot, cho phép người chơi nối các từ có 2 chữ cái theo quy tắc: chữ cái đầu của từ mới phải trùng với chữ cái cuối của từ trước.

## Tính năng

### 🎮 Game Commands
- `!start` - Bắt đầu trò chơi nối từ
- `!end` - Kết thúc trò chơi

### 👑 Admin Commands
- `!add <từ> [nghĩa]` - Thêm từ mới vào từ điển (chỉ admin)
- `!remove <từ>` - Xóa từ khỏi từ điển (chỉ admin)

## Luật chơi

1. **Từ hợp lệ**: Mỗi từ phải có đúng 2 chữ cái
2. **Quy tắc nối**: Chữ cái đầu của từ mới phải trùng với chữ cái cuối của từ trước
3. **Không lặp lại**: Không được sử dụng từ đã được nêu trước đó
4. **Thời gian**: Mỗi lượt có tối đa 30 giây để trả lời
5. **Từ điển**: Từ phải tồn tại trong cơ sở dữ liệu

## Cách chơi

1. Admin hoặc bất kỳ ai có thể bắt đầu game bằng lệnh `!start`
2. Bot sẽ chọn một từ ngẫu nhiên để bắt đầu
3. Người chơi gõ từ tiếp theo theo quy tắc nối từ
4. Bot sẽ phản hồi:
   - ✅ Nếu từ hợp lệ
   - ❌ Nếu từ không hợp lệ
5. Game tiếp tục cho đến khi hết thời gian hoặc không ai trả lời được

## Ví dụ

```
Bot: Từ đầu tiên: "ma"
User1: "an" ✅
Bot: Từ tiếp theo phải bắt đầu bằng: "N"
User2: "no" ✅
Bot: Từ tiếp theo phải bắt đầu bằng: "O"
User3: "oi" ✅
```

## Cài đặt

### Environment Variables
Thêm vào file `.env`:
```
CHANNEL_NOI_TU_ID=1234567890123456789
```

### Database
Cần có bảng `dictionary_vietnamese_two_words` với cấu trúc:
- `id` (primary key)
- `word` (varchar, unique)
- `meaning` (varchar, nullable)

## Quản lý từ điển

### Thêm từ mới
```
!add ma mẹ
!add an ăn
!add no nói
```

### Xóa từ
```
!remove ma
!remove an
```

## Lưu ý

- Chỉ hoạt động trong channel được chỉ định trong `CHANNEL_NOI_TU_ID`
- Chỉ admin mới có thể thêm/xóa từ
- Game tự động kết thúc sau 30 giây không có người trả lời
- Tất cả từ phải có trong cơ sở dữ liệu để được chấp nhận 