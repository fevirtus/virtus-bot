import discord
from datetime import datetime
from core.bot import bot, server_repo, channel_repo, channel_app_repo
from models import DiscordServer, DiscordChannel, DiscordChannelApp

@bot.tree.command(name='test', description='Test command')
async def test(interaction: discord.Interaction):
    try:
        # Get server
        server = await server_repo.get(str(interaction.guild_id))
        if server:
            await interaction.response.send_message(f"Server: {server.name}")
        else:
            await interaction.response.send_message("Server not found")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

@bot.tree.command(name='help', description='Show help')
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description="Here is a list of commands you can use:")
    embed.add_field(name="!exp", value="Show your experience points", inline=True)
    embed.add_field(name="!test", value="Test command", inline=True)
    embed.add_field(name="!help", value="Show help", inline=True)
    embed.add_field(name="!set-home-debt", value="Set channel to home debt", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="init_server", description="Khởi tạo thông tin server trong database")
async def init_server(interaction: discord.Interaction):
    """Command để khởi tạo thông tin server trong database"""
    try:
        # Kiểm tra quyền admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Bạn cần có quyền Administrator để sử dụng lệnh này!", ephemeral=True)
            return

        # Gửi response ngay lập tức
        await interaction.response.defer(ephemeral=True)

        # Kiểm tra xem server đã tồn tại trong database chưa
        existing_server = await server_repo.get_server(interaction.guild_id)
        if not existing_server:
            # Tạo record mới cho server
            await server_repo.create_server(interaction.guild_id, interaction.guild.name)
            await interaction.followup.send(f"Đã thêm server {interaction.guild.name} vào database!", ephemeral=True)
        else:
            # Cập nhật tên server nếu có thay đổi
            if existing_server.name != interaction.guild.name:
                await server_repo.update_server(interaction.guild_id, interaction.guild.name)
                await interaction.followup.send(f"Đã cập nhật tên server trong database!", ephemeral=True)
            else:
                await interaction.followup.send("Server đã tồn tại trong database!", ephemeral=True)
    except Exception as e:
        # Nếu chưa gửi response, gửi response lỗi
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)
        else:
            # Nếu đã gửi response, gửi followup
            await interaction.followup.send(f"Có lỗi xảy ra: {str(e)}", ephemeral=True)