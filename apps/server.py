import discord
from core.bot import bot, server_repo

@bot.tree.command(name='help', description='Show help')
async def help(interaction: discord.Interaction):
    """Command để hiển thị danh sách các lệnh"""
    # Get all commands
    commands = bot.tree.get_commands()
    command_list = "\n".join([f"• {c.name}: {c.description}" for c in commands])

    # Create embed with command list
    embed = discord.Embed(title="Help", description="Đây là danh sách các lệnh bạn có thể sử dụng:")
    embed.add_field(name="Danh sách lệnh", value=command_list, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)
    print(f"Đã gửi lệnh help cho {interaction.user.name}")

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