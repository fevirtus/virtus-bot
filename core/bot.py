import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from repositories import HomeDebtRepository, ScoreRepository

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
score_repo = ScoreRepository()

CHANNEL_HOME_DEBT_ID = int(os.getenv('CHANNEL_HOME_DEBT_ID', 0))

# Hỗ trợ nhiều channel cho game nối từ với format: ID1,ID2,ID3
CHANNEL_NOI_TU_IDS = []
channel_noi_tu_env = os.getenv('CHANNEL_NOI_TU_ID', '')
if channel_noi_tu_env:
    for channel_id in channel_noi_tu_env.split(','):
        try:
            CHANNEL_NOI_TU_IDS.append(int(channel_id.strip()))
        except ValueError:
            print(f"Invalid channel ID: {channel_id}")

# Giữ lại CHANNEL_NOI_TU_ID cho backward compatibility (lấy ID đầu tiên)
CHANNEL_NOI_TU_ID = CHANNEL_NOI_TU_IDS[0] if CHANNEL_NOI_TU_IDS else 0

# Admin IDs - Hỗ trợ nhiều admin với format: ID1,ID2,ID3
ADMIN_IDS = []
admin_ids_env = os.getenv('ADMIN_IDS', '')
if admin_ids_env:
    for admin_id in admin_ids_env.split(','):
        try:
            ADMIN_IDS.append(int(admin_id.strip()))
        except ValueError:
            print(f"Invalid admin ID: {admin_id}")


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
    }
    
    # Thêm help cho tất cả channel nối từ
    for channel_id in CHANNEL_NOI_TU_IDS:
        help_commands[channel_id] = [
            "!start",
            "!end",
            "!add <từ> (admin only)",
            "!remove <từ> (admin only)"
        ]
    
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