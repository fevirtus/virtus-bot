import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from repositories.config import ConfigRepository
from infra.db import postgres

# Load environment variables
load_dotenv()

from repositories.guild import GuildRepository

class VirtusBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!', 
            intents=intents,
            help_command=None # Disable default help command
        )
        
        self.config_repo = ConfigRepository()
        self.guild_repo = GuildRepository()

    async def setup_hook(self):
        # Database initialization
        await postgres.create_tables()
        
        # Load Cogs
        await self.load_extension('bot.cogs.home_debt')
        await self.load_extension('bot.cogs.score')
        await self.load_extension('bot.cogs.noi_tu')
        await self.load_extension('bot.cogs.football')
        
        # Sync Application Commands
        await self.tree.sync()
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        # Register existing guilds on startup
        for guild in self.guilds:
            await self.guild_repo.create_or_update(guild.id, guild.name)
            print(f"✅ Registered Guild: {guild.name} ({guild.id})")

    async def on_guild_join(self, guild):
        await self.guild_repo.create_or_update(guild.id, guild.name)
        print(f"👋 Joined new Guild: {guild.name} ({guild.id})")

bot = VirtusBot()