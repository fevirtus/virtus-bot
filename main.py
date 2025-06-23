import os
from dotenv import load_dotenv
from core import events, tasks
from core.bot import bot
from apps import home_debt, server, currency, noi_tu

# Load environment variables
load_dotenv()

# Run the bot
bot.run(os.getenv('BOT_TOKEN'))
