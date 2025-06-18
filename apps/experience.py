import discord
from core.bot import bot, user_repo

@bot.command(name='exp')
async def show_exp(ctx):
    user_id = ctx.author.id
    exp = await user_repo.get_exp(user_id)
    await ctx.send(f"{ctx.author.mention} has {exp} experience points!") 