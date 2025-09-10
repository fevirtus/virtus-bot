# Hướng dẫn sử dụng Bot với nhiều Channel

## Tổng quan

Bot đã được refactor để hỗ trợ chạy game nối từ trên nhiều channel đồng thời với cùng một bot token.

## Cấu hình Environment Variables

### Format đơn giản với dấu phẩy

```bash
# Nhiều channel, phân cách bằng dấu phẩy (không có khoảng trắng)
CHANNEL_NOI_TU_ID=1383424686708363336,9876543210987654321,5555555555555555555
```

### Ví dụ thực tế

```bash
# 1 channel
CHANNEL_NOI_TU_ID=1383424686708363336

# 2 channel
CHANNEL_NOI_TU_ID=1383424686708363336,9876543210987654321

# 3 channel
CHANNEL_NOI_TU_ID=1383424686708363336,9876543210987654321,5555555555555555555
```

### Lưu ý
- Không có khoảng trắng xung quanh dấu phẩy
- Mỗi ID phải là số nguyên hợp lệ
- Bot sẽ tự động parse và hỗ trợ tất cả channel trong danh sách

## Cách hoạt động

### Game State riêng biệt
- Mỗi channel có game state hoàn toàn độc lập
- Channel A có thể đang chơi game với từ "âm cao" → "cao độ"
- Channel B có thể đang chơi game khác với từ "mặt trời" → "trời mưa"
- Không có xung đột giữa các game

### Database chung
- Tất cả channel sử dụng chung database PostgreSQL
- Từ điển nối từ được chia sẻ giữa các channel
- Admin có thể thêm/xóa từ từ bất kỳ channel nào

## Lệnh hỗ trợ

### Lệnh cơ bản
- `!start` - Bắt đầu game nối từ
- `!end` - Kết thúc game nối từ

### Lệnh admin (chỉ admin server)
- `!add <từ>` - Thêm từ mới vào database
- `!remove <từ>` - Xóa từ khỏi database

### Lệnh khác
- `/help` - Hiển thị danh sách lệnh cho channel hiện tại

## Ví dụ sử dụng

### Server A (Channel #game-1)
```
User: !start
Bot: 🎮 Trò chơi Nối Từ đã bắt đầu!
     Từ đầu tiên: âm cao

User: cao độ
Bot: ✅

User: độ cao
Bot: ✅
```

### Server B (Channel #game-2) - Đồng thời
```
User: !start
Bot: 🎮 Trò chơi Nối Từ đã bắt đầu!
     Từ đầu tiên: mặt trời

User: trời mưa
Bot: ✅

User: mưa gió
Bot: ✅
```

## Lưu ý quan trọng

1. **Bot Token**: Chỉ cần 1 bot token duy nhất
2. **Database**: Tất cả channel dùng chung database
3. **Game State**: Mỗi channel có game state riêng biệt
4. **Admin**: Admin của server có thể quản lý từ điển
5. **Timeout**: Mỗi game có timeout 30 giây độc lập

## Troubleshooting

### Bot không phản hồi trong channel
- Kiểm tra channel ID có trong `CHANNEL_NOI_TU_IDS` không
- Kiểm tra bot có quyền gửi tin nhắn trong channel không

### Game không bắt đầu được
- Kiểm tra xem đã có game đang chạy trong channel đó chưa
- Kiểm tra database có từ nào không

### Lỗi database
- Kiểm tra kết nối PostgreSQL
- Kiểm tra biến môi trường database
