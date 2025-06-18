from discord.ext import tasks
from datetime import datetime
from .bot import bot, user_repo, active_voice_users, VOICE_EXP_POINTS_PER_MINUTE

@tasks.loop(minutes=1)
async def update_voice_exp():
    current_time = datetime.now()
    for user_id in list(active_voice_users):
        last_join_time = await user_repo.get_voice_time(user_id)
        if last_join_time:
            join_time = datetime.fromisoformat(last_join_time)
            time_spent = current_time - join_time
            if time_spent.total_seconds() >= 60:
                current_exp = await user_repo.get_exp(user_id)
                new_exp = current_exp + VOICE_EXP_POINTS_PER_MINUTE
                await user_repo.update_exp(user_id, new_exp)
                await user_repo.update_voice_time(user_id, current_time.isoformat())
                print(f"Added {VOICE_EXP_POINTS_PER_MINUTE} exp points to user {user_id} for voice time") 