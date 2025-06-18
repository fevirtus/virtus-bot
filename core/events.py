from datetime import datetime
from .bot import bot, user_repo, user_cooldowns, active_voice_users, CHAT_EXP_POINTS, CHAT_COOLDOWN, VOICE_EXP_POINTS_PER_MINUTE

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    from .tasks import update_voice_exp
    update_voice_exp.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Handle chat experience points
    user_id = message.author.id
    current_time = datetime.now()
    
    if user_id not in user_cooldowns or (current_time - user_cooldowns[user_id]).total_seconds() >= CHAT_COOLDOWN:
        current_exp = await user_repo.get_exp(user_id)
        new_exp = current_exp + CHAT_EXP_POINTS
        await user_repo.update_exp(user_id, new_exp)
        user_cooldowns[user_id] = current_time
        print(f"Added {CHAT_EXP_POINTS} exp points to {message.author.name}. Total: {new_exp}")

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    # User joined a voice channel
    if before.channel is None and after.channel is not None:
        current_time = datetime.now().isoformat()
        await user_repo.update_voice_time(member.id, current_time)
        active_voice_users.add(member.id)
        print(f"{member.name} joined voice channel {after.channel.name}")

    # User left a voice channel
    elif before.channel is not None and after.channel is None:
        if member.id in active_voice_users:
            active_voice_users.remove(member.id)
            last_join_time = await user_repo.get_voice_time(member.id)
            if last_join_time:
                join_time = datetime.fromisoformat(last_join_time)
                time_spent = datetime.now() - join_time
                minutes = int(time_spent.total_seconds() / 60)
                exp_points = minutes * VOICE_EXP_POINTS_PER_MINUTE
                current_exp = await user_repo.get_exp(member.id)
                new_exp = current_exp + exp_points
                await user_repo.update_exp(member.id, new_exp)
                print(f"{member.name} spent {minutes} minutes in voice. Added {exp_points} exp points. Total: {new_exp}") 