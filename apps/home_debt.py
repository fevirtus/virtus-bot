import discord
from datetime import datetime
from core.bot import bot, server_repo, channel_repo, channel_app_repo, home_debt_repo
from models import DiscordServer, DiscordChannel, DiscordChannelApp

@bot.tree.command(name='set-home-debt', description='Set channel to home debt')
async def set_home_debt(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        # Get or create server
        server = await server_repo.get(str(interaction.guild_id))
        if not server:
            server = DiscordServer(
                id=str(interaction.guild_id),
                name=interaction.guild.name,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            server = await server_repo.create(server)

        # Get or create channel
        discord_channel = await channel_repo.get(str(channel.id))
        if not discord_channel:
            discord_channel = DiscordChannel(
                id=str(channel.id),
                server_id=str(interaction.guild_id),
                name=channel.name,
                type='text',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            discord_channel = await channel_repo.create(discord_channel)

        # Create or update home debt app
        apps = await channel_app_repo.get_by_channel(str(channel.id))
        home_debt_app = next((app for app in apps if app.app_type == 'home_debt'), None)
        
        if home_debt_app:
            home_debt_app.config = {'enabled': True}
            await channel_app_repo.update(home_debt_app)
        else:
            home_debt_app = DiscordChannelApp(
                id=f"{channel.id}_home_debt",
                channel_id=str(channel.id),
                app_type='home_debt',
                config={'enabled': True},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            await channel_app_repo.create(home_debt_app)

        await interaction.response.send_message(f"Home debt app has been set up for {channel.mention}")
    except Exception as e:
        await interaction.response.send_message(f"Error setting up home debt app: {str(e)}")

@bot.tree.command(name="add_member", description="Thêm thành viên mới vào nhà")
async def add_member(interaction: discord.Interaction, member: discord.Member):
    """Thêm thành viên mới vào nhà"""
    try:
        # Kiểm tra xem thành viên đã tồn tại chưa
        existing_member = await home_debt_repo.get_member(member.id)
        if existing_member:
            await interaction.response.send_message(f"Thành viên {member.name} đã tồn tại trong hệ thống!", ephemeral=True)
            return

        # Thêm thành viên mới
        await home_debt_repo.add_member(member.id, member.name)
        await interaction.response.send_message(f"Đã thêm thành viên {member.name} vào hệ thống!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="add_expense", description="Thêm khoản chi tiêu mới")
async def add_expense(interaction: discord.Interaction, amount: float, description: str):
    """Thêm khoản chi tiêu mới"""
    try:
        # Kiểm tra xem người dùng có phải là thành viên không
        member = await home_debt_repo.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message("Bạn chưa được thêm vào hệ thống! Vui lòng sử dụng lệnh /add_member trước.", ephemeral=True)
            return

        # Thêm khoản chi tiêu
        expense = await home_debt_repo.add_expense(amount, description, interaction.user.id)
        await interaction.response.send_message(f"Đã thêm khoản chi tiêu: {description} - {amount}đ", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="check_balance", description="Kiểm tra số dư của bạn")
async def check_balance(interaction: discord.Interaction):
    """Kiểm tra số dư của bạn"""
    try:
        # Kiểm tra xem người dùng có phải là thành viên không
        member = await home_debt_repo.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message("Bạn chưa được thêm vào hệ thống! Vui lòng sử dụng lệnh /add_member trước.", ephemeral=True)
            return

        # Lấy số dư
        balance = await home_debt_repo.get_balance(interaction.user.id)
        await interaction.response.send_message(f"Số dư của bạn: {balance}đ", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)

@bot.tree.command(name="list_expenses", description="Xem danh sách chi tiêu")
async def list_expenses(interaction: discord.Interaction):
    """Xem danh sách chi tiêu"""
    try:
        # Kiểm tra xem người dùng có phải là thành viên không
        member = await home_debt_repo.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message("Bạn chưa được thêm vào hệ thống! Vui lòng sử dụng lệnh /add_member trước.", ephemeral=True)
            return

        # Lấy danh sách chi tiêu
        expenses = await home_debt_repo.get_expenses()
        if not expenses:
            await interaction.response.send_message("Chưa có khoản chi tiêu nào!", ephemeral=True)
            return

        # Tạo embed message
        embed = discord.Embed(title="Danh sách chi tiêu", color=discord.Color.blue())
        for expense in expenses:
            member = await home_debt_repo.get_member(expense.member_id)
            embed.add_field(
                name=f"{expense.description} - {expense.amount}đ",
                value=f"Người chi: {member.name}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True) 