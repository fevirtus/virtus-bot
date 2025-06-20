import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize repositories
from repositories import ServerRepository, ChannelRepository, ChannelAppRepository, HomeDebtRepository

server_repo = ServerRepository()
channel_repo = ChannelRepository()
channel_app_repo = ChannelAppRepository()
home_debt_repo = HomeDebtRepository()

# Store user cooldowns
from typing import Dict, Set
from datetime import datetime

user_cooldowns: Dict[int, datetime] = {}
active_voice_users: Set[int] = set()

# Constants
CHAT_EXP_POINTS = 1
VOICE_EXP_POINTS_PER_MINUTE = 2
CHAT_COOLDOWN = 60  # seconds 