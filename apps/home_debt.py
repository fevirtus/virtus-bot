import discord
from core.bot import bot, home_debt_repo, CHANNEL_HOME_DEBT_ID
from utils.common import format_vnd


def is_correct_channel(ctx):
    """Kiểm tra xem command có được thực hiện trong đúng channel không"""
    return ctx.channel.id == CHANNEL_HOME_DEBT_ID

@bot.command(name="hdadd", description="Thêm khoản chi tiêu mới")
async def add(ctx, amount: int):
    """Vì home chỉ có 2 người nên sẽ tự động thêm khoản chi tiêu cho người còn lại"""
    try:
        if not is_correct_channel(ctx):
            return
        
        # Get info other user from home_debt table
        other_user = await home_debt_repo.get_other(ctx.author.id)
        other_user.value += round(amount / 2)
        resp = await home_debt_repo.update_home_debt(other_user)
        if not resp:
            await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu")
            return
        
        await ctx.send(f"Đã thêm {format_vnd(round(amount * 1000 / 2))} cho {ctx.author.name}. Số dư hiện tại là {format_vnd(other_user.value * 1000)}")
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {str(e)}")

@bot.command(name="hdcheck", description="Kiểm tra số dư của bạn")
async def home_debt_check(ctx):
    """Kiểm tra số dư của mọi người"""
    try:
        if not is_correct_channel(ctx):
            return
        
        # Get info user from home_debt table
        users = await home_debt_repo.get_all()
        embed = discord.Embed(title="Số dư của mọi người", color=discord.Color.blue())
        for user in users:
            value = format_vnd(user.value * 1000)
            embed.add_field(name=f"{ctx.guild.get_member(user.user_id).display_name}", value=f"{value}", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {str(e)}")

@bot.command(name="hdvay", description="Vay nợ")
async def vay(ctx, amount: int):
    """Vay nợ"""
    try:
        if not is_correct_channel(ctx):
            return
        
        # Get info user from home_debt table
        user = await home_debt_repo.get(ctx.author.id)
        user.value += amount
        resp = await home_debt_repo.update_home_debt(user)
        if not resp:
            await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu")
            return
        
        # Send message to user
        await ctx.send(f"Đã vay {format_vnd(amount * 1000)} bởi {ctx.author.name}")
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {str(e)}")

@bot.command(name="hdtra", description="Trả nợ")
async def tra(ctx, amount: int):
    """Trả nợ"""
    try:
        if not is_correct_channel(ctx):
            return
        
        # Get info user from home_debt table
        user = await home_debt_repo.get(ctx.author.id)
        user.value -= amount
        resp = await home_debt_repo.update_home_debt(user)
        if not resp:
            await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu")
            return
        
        # Send message to user
        await ctx.send(f"Đã trả {format_vnd(amount * 1000)} từ {ctx.author.name}")
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {str(e)}")