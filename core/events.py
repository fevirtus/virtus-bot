import discord
from core.bot import bot
from core.tasks import sync_commands

# Using for sync commands to all guilds
@bot.event
async def on_ready():
    print(f'{bot.user} đã tham gia vào server!')
    await sync_commands.start()
    print("Đã đồng bộ lệnh!")

# @bot.event
# async def on_ready():
#     guild_id = 536422615649091595
#     guild_obj = discord.Object(id=guild_id)

#     try:
#         synced = await bot.tree.sync(guild=guild_obj)
#         print(f"🔁 Synced {len(synced)} command(s) to guild {guild_id}")
#     except Exception as e:
#         print(f"❌ Failed to sync commands to guild {guild_id}: {e}")