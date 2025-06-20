import discord
from core.bot import bot, server_repo, channel_repo, home_debt_repo
from utils.common import format_vnd

@bot.tree.command(name='set-home-debt', description='Set channel to home debt')
async def set_home_debt(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        # Kiểm tra xem người dùng có quyền admin không
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Bạn cần có quyền Administrator để sử dụng lệnh này!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)
        
        # Ensure server is in database
        server = await server_repo.get(str(interaction.guild_id))
        if not server:
            await interaction.followup.send("Server chưa được khởi tạo trong database! Vui lòng sử dụng lệnh /init_server trước.", ephemeral=True)
            return

        # Ensure channel was registered in database
        discord_channel = await channel_repo.get_channel(channel.id)
        if not discord_channel:
            await channel_repo.create_channel(interaction.guild_id, channel.id, 'home_debt')
        else:
            await channel_repo.update_channel(channel.id, 'home_debt')

        await interaction.followup.send(f"home_debt app đã được cấu hình cho {channel.mention}")
    except Exception as e:
        if interaction.response.is_done():
            await interaction.followup.send(f"Lỗi khi cấu hình home_debt app: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Lỗi khi cấu hình home_debt app: {str(e)}", ephemeral=True)

# Check if the channel is registered and configured for home_debt app
async def check_channel_home_debt(channel_id: int) -> bool:
    # Check if channel is registered in database
    channel = await channel_repo.get_channel(channel_id)
    if not channel or channel.app != 'home_debt':
        return False
    
    return True

@bot.tree.command(name="home-debt-add", description="Thêm khoản chi tiêu mới")
async def home_debt_add(interaction: discord.Interaction, amount: int, description: str = "Không có lý do"):
    """Vì home chỉ có 2 người nên sẽ tự động thêm khoản chi tiêu cho người còn lại"""
    try:
        check = await check_channel_home_debt(interaction.channel_id)
        if not check:
            await interaction.response.send_message("Channel chưa được đăng ký!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        
        # Get info other user from home_debt table
        other_user = await home_debt_repo.get_other(interaction.user.id)
        other_user.value += round(amount / 2)
        resp = await home_debt_repo.update_home_debt(other_user)
        if not resp:
            await interaction.followup.send("Có lỗi xảy ra khi cập nhật dữ liệu", ephemeral=True)
            return
        
        await interaction.followup.send(f"Đã thêm {format_vnd(round(amount * 1000 / 2))} cho {interaction.user.name}. Số dư hiện tại là {format_vnd(other_user.value * 1000)}", ephemeral=False)
    except Exception as e:
        if interaction.response.is_done():
            await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="home-debt-check", description="Kiểm tra số dư của bạn")
async def home_debt_check(interaction: discord.Interaction):
    """Kiểm tra số dư của mọi người"""
    try:
        check = await check_channel_home_debt(interaction.channel_id)
        if not check:
            await interaction.response.send_message("Channel chưa được đăng ký!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        # Lấy số dư của mọi người
        home_debts = await home_debt_repo.get_all()
        embed = discord.Embed(title="Số dư của mọi người", color=discord.Color.blue())
        for home_debt in home_debts:
            user = await bot.fetch_user(home_debt.user_id)
            value = format_vnd(home_debt.value * 1000)
            embed.add_field(name=f"{user.name}", value=f"{value}", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=False)
    except Exception as e:
        if interaction.response.is_done():
            await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="vay-debt", description="Vay nợ")
async def vay_debt(interaction: discord.Interaction, amount: int, description: str = "Không có lý do"):
    """Vay nợ"""
    try:
        check = await check_channel_home_debt(interaction.channel_id)
        if not check:
            await interaction.response.send_message("Channel chưa được đăng ký!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        
        # Get info user from home_debt table
        user = await home_debt_repo.get(interaction.user.id)
        user.value += amount
        resp = await home_debt_repo.update_home_debt(user)
        if not resp:
            await interaction.followup.send("Có lỗi xảy ra khi cập nhật dữ liệu", ephemeral=True)
            return
        
        # Send message to user
        await interaction.followup.send(f"Đã vay {format_vnd(amount * 1000)} bởi {interaction.user.name}", ephemeral=False)
    except Exception as e:
        if interaction.response.is_done():
            await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="tra-debt", description="Trả nợ")
async def tra_debt(interaction: discord.Interaction, amount: int):
    """Trả nợ"""
    try:
        check = await check_channel_home_debt(interaction.channel_id)
        if not check:
            await interaction.response.send_message("Channel chưa được đăng ký!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        
        # Get info user from home_debt table
        user = await home_debt_repo.get(interaction.user.id)
        user.value -= amount
        resp = await home_debt_repo.update_home_debt(user)
        if not resp:
            await interaction.followup.send("Có lỗi xảy ra khi cập nhật dữ liệu", ephemeral=True)
            return
        
        # Send message to user
        await interaction.followup.send(f"Đã trả {format_vnd(amount * 1000)} từ {interaction.user.name}", ephemeral=False)
    except Exception as e:
        if interaction.response.is_done():
            await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)