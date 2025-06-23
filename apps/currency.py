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