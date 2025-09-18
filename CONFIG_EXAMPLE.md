# Ví dụ cấu hình .env

## Format cơ bản

```bash
# Bot Token
BOT_TOKEN=your_bot_token_here

# Database Configuration
POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/database_name

# Channel IDs
CHANNEL_HOME_DEBT_ID=1234567890123456789

# Game Nối Từ - Hỗ trợ nhiều channel với dấu phẩy
CHANNEL_NOI_TU_ID=1383424686708363336,9876543210987654321,5555555555555555555

# Admin IDs - Hỗ trợ nhiều admin với dấu phẩy
ADMIN_IDS=123456789012345678,987654321098765432
```

## Các ví dụ khác nhau

### 1 channel
```bash
CHANNEL_NOI_TU_ID=1383424686708363336
```

### 2 channel
```bash
CHANNEL_NOI_TU_ID=1383424686708363336,9876543210987654321
```

### 3+ channel
```bash
CHANNEL_NOI_TU_ID=1383424686708363336,9876543210987654321,5555555555555555555
```

### Admin IDs
```bash
# 1 admin
ADMIN_IDS=123456789012345678

# 2 admin
ADMIN_IDS=123456789012345678,987654321098765432

# 3+ admin
ADMIN_IDS=123456789012345678,987654321098765432,555555555555555555
```

## Lưu ý quan trọng

- ✅ **Đúng**: `CHANNEL_NOI_TU_ID=123,456,789`
- ❌ **Sai**: `CHANNEL_NOI_TU_ID=123, 456, 789` (có khoảng trắng)
- ❌ **Sai**: `CHANNEL_NOI_TU_ID="123,456,789"` (có dấu ngoặc kép)
- ❌ **Sai**: `CHANNEL_NOI_TU_ID=123,abc,789` (có ký tự không phải số)

- ✅ **Đúng**: `ADMIN_IDS=123456789,987654321`
- ❌ **Sai**: `ADMIN_IDS=123456789, 987654321` (có khoảng trắng)
- ❌ **Sai**: `ADMIN_IDS="123456789,987654321"` (có dấu ngoặc kép)
- ❌ **Sai**: `ADMIN_IDS=123456789,abc123` (có ký tự không phải số)

## Cách test

1. Cập nhật file `.env` với format mới
2. Restart bot
3. Kiểm tra log để xem bot có parse đúng channel IDs không
4. Test `!start` trong từng channel để đảm bảo hoạt động
