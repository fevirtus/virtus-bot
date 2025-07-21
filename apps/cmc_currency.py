import discord
from core.bot import bot, CHANNEL_CMC_CURRENCY_ID, OWNER_CHANNEL_CMC_CURRENCY_ID
from utils.common import format_vnd
from repositories.debt import DebtRepository
from discord.ext import commands
import math

# Sử dụng quyền admin hoặc owner để xác định chủ nhóm

debt_repo = DebtRepository()

def is_correct_channel(ctx):
    """Kiểm tra xem command có được thực hiện trong đúng channel không"""
    return ctx.channel.id == CHANNEL_CMC_CURRENCY_ID

def is_owner(ctx: commands.Context):
    """Kiểm tra xem user có phải là chủ nhóm không"""
    return ctx.author.id == OWNER_CHANNEL_CMC_CURRENCY_ID

@bot.command(name="zadd")
async def zadd(ctx: commands.Context, amount: int, *names):
    if not is_correct_channel(ctx):
        return
    if not is_owner(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này!")
        return
    if not names:
        await ctx.send("Bạn phải nhập ít nhất 1 tên!")
        return
    per_person = int(math.ceil(amount / len(names)))
    msg = f"Chia {format_vnd(amount*1000)} cho {len(names)} người, mỗi người: {format_vnd(per_person*1000)}\n"
    await ctx.send(msg)

@bot.command(name="zminus")
async def zminus(ctx: commands.Context, name: str, amount: int):
    if not is_correct_channel(ctx):
        return
    await debt_repo.minus_debt(name, amount)
    await ctx.send(f"Đã trừ {format_vnd(amount*1000)} cho {name}")

@bot.command(name="zcheck")
async def zcheck(ctx: commands.Context):
    if not is_correct_channel(ctx):
        return
    debts = await debt_repo.get_all()
    if not debts:
        await ctx.send("Không ai nợ chủ nhóm!")
        return
    msg = "Tình hình nợ hiện tại:\n"
    for d in debts:
        msg += f"{d.name}: {format_vnd(d.amount*1000)}\n"
    await ctx.send(msg)

