import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Set

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store user cooldowns and experience points
user_cooldowns: Dict[int, datetime] = {}
user_exp_points: Dict[int, int] = {}
voice_time: Dict[int, datetime] = {}
active_voice_users: Set[int] = set()

# Constants
CHAT_EXP_POINTS = 1
VOICE_EXP_POINTS_PER_MINUTE = 2
CHAT_COOLDOWN = 60  # seconds

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    update_voice_exp.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Handle chat experience points
    user_id = message.author.id
    current_time = datetime.now()
    
    if user_id not in user_cooldowns or (current_time - user_cooldowns[user_id]).total_seconds() >= CHAT_COOLDOWN:
        user_exp_points[user_id] = user_exp_points.get(user_id, 0) + CHAT_EXP_POINTS
        user_cooldowns[user_id] = current_time
        print(f"Added {CHAT_EXP_POINTS} exp points to {message.author.name}. Total: {user_exp_points[user_id]}")

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    # User joined a voice channel
    if before.channel is None and after.channel is not None:
        voice_time[member.id] = datetime.now()
        active_voice_users.add(member.id)
        print(f"{member.name} joined voice channel {after.channel.name}")

    # User left a voice channel
    elif before.channel is not None and after.channel is None:
        if member.id in active_voice_users:
            active_voice_users.remove(member.id)
            if member.id in voice_time:
                time_spent = datetime.now() - voice_time[member.id]
                minutes = int(time_spent.total_seconds() / 60)
                exp_points = minutes * VOICE_EXP_POINTS_PER_MINUTE
                user_exp_points[member.id] = user_exp_points.get(member.id, 0) + exp_points
                print(f"{member.name} spent {minutes} minutes in voice. Added {exp_points} exp points. Total: {user_exp_points[member.id]}")
                del voice_time[member.id]

@tasks.loop(minutes=1)
async def update_voice_exp():
    current_time = datetime.now()
    for user_id in list(active_voice_users):
        if user_id in voice_time:
            time_spent = current_time - voice_time[user_id]
            if time_spent.total_seconds() >= 60:
                user_exp_points[user_id] = user_exp_points.get(user_id, 0) + VOICE_EXP_POINTS_PER_MINUTE
                voice_time[user_id] = current_time
                print(f"Added {VOICE_EXP_POINTS_PER_MINUTE} exp points to user {user_id} for voice time")

@bot.command(name='exp')
async def show_exp(ctx):
    user_id = ctx.author.id
    exp = user_exp_points.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention} has {exp} experience points!")

print(f"Token: {repr(os.getenv('BOT_TOKEN'))}")
# Run the bot
bot.run(os.getenv('BOT_TOKEN'))
