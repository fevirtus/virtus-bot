import discord
from core.bot import bot
# from core.tasks import sync_commands

# Using for sync commands to all guilds
@bot.event
async def on_ready():
    print(f'{bot.user} đã tham gia vào server!')
    # await sync_commands.start()
    TEST_GUILD_ID = discord.Object(id=536422615649091595)
    await bot.tree.sync(guild=TEST_GUILD_ID)
    print("Đã đồng bộ lệnh!")