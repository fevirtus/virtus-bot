from core.bot import bot
from core.tasks import sync_commands

@bot.event
async def on_ready():
    print(f'{bot.user} đã tham gia vào server!')
    await sync_commands.start()
    print("Đã đồng bộ lệnh!")