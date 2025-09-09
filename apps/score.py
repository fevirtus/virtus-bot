import discord
from discord.ext import commands
from core.bot import bot, score_repo

@bot.command(name="ncheck", description="Kiểm tra thông tin tài khoản của bạn")
async def score_check(ctx: commands.Context):
    """Kiểm tra thông tin tài khoản của bạn"""
    # Check if user is registered in database. If not, create a new one
    score = await score_repo.get(ctx.author.id)
    if not score:
        await ctx.send("Bạn chưa có tài khoản score")
        await score_repo.create(ctx.author.id, 0)
        score = await score_repo.get(ctx.author.id)
        
        # Kiểm tra lại sau khi tạo
        if not score:
            await ctx.send("Có lỗi xảy ra khi tạo tài khoản score")
            return

    await ctx.send(f"Thông tin tài khoản của bạn: {score.point}")

@bot.command(name="rank", description="list rank")
async def list_rank(ctx: commands.Context):
    """Kiểm tra thông tin tài khoản của bạn"""
    # Check if user is registered in database. If not, create a new one
    points = await score_repo.get_all()
    msg = "```\n"
    msg += f"{'No.':<4} {'Name':<20} {'Win':>8}\n"
    msg += "-" * 34 + "\n"
    for i, b in enumerate(points, start=1):
        msg += f"{i:<4} {b.user_name:<20} {b.point:>8}\n"
    msg += "```"

    await ctx.send(msg)

async def incr(user_id, user_name, amount):
    await score_repo.upsert_or_increment_point(user_id, user_name, amount)

