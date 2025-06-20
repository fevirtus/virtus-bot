from discord.ext import tasks
from core.bot import bot

# @tasks.loop(minutes=1)
# async def update_voice_exp():
#     current_time = datetime.now()
#     for user_id in list(active_voice_users):
#         last_join_time = await user_repo.get_voice_time(user_id)
#         if last_join_time:
#             join_time = datetime.fromisoformat(last_join_time)
#             time_spent = current_time - join_time
#             if time_spent.total_seconds() >= 60:
#                 current_exp = await user_repo.get_exp(user_id)
#                 new_exp = current_exp + VOICE_EXP_POINTS_PER_MINUTE
#                 await user_repo.update_exp(user_id, new_exp)
#                 await user_repo.update_voice_time(user_id, current_time.isoformat())
#                 print(f"Thêm {VOICE_EXP_POINTS_PER_MINUTE} điểm kinh nghiệm cho user {user_id} cho thời gian voice") 

@tasks.loop(minutes=1)
async def sync_commands():
    await bot.tree.sync()
    print("Đã đồng bộ lệnh!")