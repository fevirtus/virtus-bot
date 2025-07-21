import os
from dotenv import load_dotenv
from core import events, tasks
from core.bot import bot
from apps import home_debt, currency, noi_tu, cmc_currency

# Load environment variables
load_dotenv()

# Run the bot
bot.run(os.getenv('BOT_TOKEN'))
