import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from repositories import HomeDebtRepository, CurrencyRepository

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
home_debt_repo = HomeDebtRepository()
currency_repo = CurrencyRepository()

CHANNEL_HOME_DEBT_ID = int(os.getenv('CHANNEL_HOME_DEBT_ID', 0))
CHANNEL_NOI_TU_ID = int(os.getenv('CHANNEL_NOI_TU_ID', 0))
CHANNEL_CMC_CURRENCY_ID = int(os.getenv('CHANNEL_CMC_CURRENCY_ID', 0))
OWNER_CHANNEL_CMC_CURRENCY_ID = int(os.getenv('OWNER_CHANNEL_CMC_CURRENCY_ID', 0))


@bot.tree.command(name='help', description='Show help')
async def help(interaction: discord.Interaction):
    """Command để hiển thị danh sách các lệnh"""
    channel = interaction.channel
    
    # Dictionary chứa thông tin help cho từng channel
    help_commands = {
        CHANNEL_HOME_DEBT_ID: [
            "!hdadd <số tiền>",
            "!hdcheck", 
            "!hdtra <số tiền>",
            "!hdvay <số tiền>"
        ],
        CHANNEL_NOI_TU_ID: [
            "!start",
            "!end"
        ],
    }
    
    # Kiểm tra xem channel có trong danh sách không
    if channel.id in help_commands:
        embed = discord.Embed(
            title="Help", 
            description="Đây là danh sách các lệnh bạn có thể sử dụng:", 
            color=discord.Color.blue()
        )
        
        commands_list = "\n".join(help_commands[channel.id])
        embed.add_field(name="", value=commands_list, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
    else:
        await interaction.response.send_message(
            "Không có lệnh help cho channel này!", 
            ephemeral=True
        )