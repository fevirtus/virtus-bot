import discord
from discord.ext import commands
from core.bot import bot, currency_repo

@bot.command(name="ncheck", description="Kiểm tra thông tin tài khoản của bạn")
async def currency_check(ctx: commands.Context):
    """Kiểm tra thông tin tài khoản của bạn"""
    # Check if user is registered in database. If not, create a new one
    currency = await currency_repo.get(ctx.author.id)
    if not currency:
        await ctx.send("Bạn chưa có tài khoản currency")
        await currency_repo.create(ctx.author.id, 0)
        currency = await currency_repo.get(ctx.author.id)
        
        # Kiểm tra lại sau khi tạo
        if not currency:
            await ctx.send("Có lỗi xảy ra khi tạo tài khoản currency")
            return

    await ctx.send(f"Thông tin tài khoản của bạn: {currency.balance}")

@bot.command(name="rank", description="list rank")
async def list_rank(ctx: commands.Context):
    """Kiểm tra thông tin tài khoản của bạn"""
    # Check if user is registered in database. If not, create a new one
    balances = await currency_repo.get_all()
    msg = "```\n"
    msg += f"{'No.':<4} {'Name':<20} {'Win':>8}\n"
    msg += "-" * 34 + "\n"
    for i, b in enumerate(balances, start=1):
        msg += f"{i:<4} {b.user_name:<20} {b.balance:>8}\n"
    msg += "```"

    await ctx.send(msg)

async def incr(user_id, user_name, amount):
    await currency_repo.upsert_or_increment_balance(user_id, user_name, amount)

