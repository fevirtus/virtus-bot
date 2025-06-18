import os
from dotenv import load_dotenv
from core.bot import bot
from core import events, tasks
from apps import experience, server

# Load environment variables
load_dotenv()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
