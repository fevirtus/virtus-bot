import discord
from typing import Any
from core.bot import bot, server_repo, channel_repo, home_debt_repo

@bot.tree.command(name='set-home-debt', description='Set channel to home debt')
async def set_home_debt(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        # Kiểm tra xem người dùng có quyền admin không
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Bạn cần có quyền Administrator để sử dụng lệnh này!", ephemeral=True)
            return

        # Ensure server is in database
        server = await server_repo.get(str(interaction.guild_id))
        if not server:
            await interaction.response.send_message("Server chưa được khởi tạo trong database! Vui lòng sử dụng lệnh /init_server trước.", ephemeral=True)
            return

        # Ensure channel was registered in database
        discord_channel = await channel_repo.get_channel(channel.id)
        if not discord_channel:
            await channel_repo.create_channel(interaction.guild_id, channel.id, 'home_debt')
        else:
            await channel_repo.update_channel(channel.id, 'home_debt')

        await interaction.response.send_message(f"home_debt app đã được cấu hình cho {channel.mention}")
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi cấu hình home_debt app: {str(e)}")

# Decorator to check if the channel is registered and configured for home_debt app
def check_channel_home_debt():
    def decorator(func):
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            channel = await channel_repo.get_channel(interaction.channel_id)
            if not channel:
                await interaction.response.send_message("Channel chưa được đăng ký!", ephemeral=True)
                return
            if channel.app != 'home_debt':
                await interaction.response.send_message("Lệnh này chỉ có thể sử dụng trong channel đã được cấu hình cho home_debt app!", ephemeral=True)
                return
            await func(interaction, *args, **kwargs)
        return wrapper
    return decorator

@bot.tree.command(name="home-debt-add", description="Thêm khoản chi tiêu mới")
# @check_channel_home_debt()
async def home_debt_add(interaction: discord.Interaction, amount: float, description: str):
    """Vì home chỉ có 2 người nên sẽ tự động thêm khoản chi tiêu cho người còn lại"""
    try:
        # Get info other user from home_debt table
        other_user = await home_debt_repo.get_other(interaction.user.id)
        other_user.value += amount / 2
        await home_debt_repo.update_home_debt(other_user)
        await interaction.response.send_message(f"Đã thêm khoản chi tiêu: {description} - {amount / 2}đ cho {other_user.user_id}", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="home-debt-check", description="Kiểm tra số dư của bạn")
async def home_debt_check(interaction: discord.Interaction):
    """Kiểm tra số dư của mọi người"""
    try:
        # Lấy số dư của mọi người
        home_debts = await home_debt_repo.get_all()
        await interaction.response.send_message(f"Số dư của mọi người: {home_debts}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="vay-debt", description="Vay nợ")
async def vay_debt(interaction: discord.Interaction, amount: float, description: str):
    """Vay nợ"""
    try:
        # Get info user from home_debt table
        user = await home_debt_repo.get(interaction.user.id)
        user.value += amount
        await home_debt_repo.update_home_debt(user)

        # Send message to user
        await interaction.response.send_message(f"Đã vay nợ: {description} - {amount}đ cho {user.user_id}", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="tra-debt", description="Trả nợ")
async def tra_debt(interaction: discord.Interaction, amount: float):
    """Trả nợ"""
    try:
        # Get info user from home_debt table
        user = await home_debt_repo.get(interaction.user.id)
        user.value -= amount
        await home_debt_repo.update_home_debt(user)

        # Send message to user
        await interaction.response.send_message(f"Đã trả nợ: {amount}đ cho {user.user_id}", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)