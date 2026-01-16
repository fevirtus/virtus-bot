import discord
from discord.ext import commands
from repositories import ScoreRepository
from repositories.feature_toggle import FeatureToggleRepository

class ScoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.score_repo = ScoreRepository()
        self.feature_repo = FeatureToggleRepository()

    async def is_enabled(self, guild_id: int) -> bool:
        return await self.feature_repo.get(guild_id, "score")

    @commands.command(name="ncheck", description="Kiểm tra thông tin tài khoản của bạn")
    async def score_check(self, ctx: commands.Context):
        """Kiểm tra thông tin tài khoản của bạn"""
        if not await self.is_enabled(ctx.guild.id):
            return

        # Check if user is registered in database. If not, create a new one
        score = await self.score_repo.get(ctx.guild.id, ctx.author.id)
        if not score:
            await ctx.send("Bạn chưa có tài khoản score")
            await self.score_repo.create(ctx.guild.id, ctx.author.id, 0)
            score = await self.score_repo.get(ctx.guild.id, ctx.author.id)
            
            # Kiểm tra lại sau khi tạo
            if not score:
                await ctx.send("Có lỗi xảy ra khi tạo tài khoản score")
                return

        await ctx.send(f"Thông tin tài khoản của bạn: {score.point}")

    @commands.command(name="rank", description="list rank")
    async def list_rank(self, ctx: commands.Context):
        """Kiểm tra rank"""
        if not await self.is_enabled(ctx.guild.id):
            return

        points = await self.score_repo.get_all(ctx.guild.id)
        msg = "```\n"
        msg += f"{'No.':<4} {'Name':<20} {'Win':>8}\n"
        msg += "-" * 34 + "\n"
        for i, b in enumerate(points, start=1):
            msg += f"{i:<4} {b.user_name:<20} {b.point:>8}\n"
        msg += "```"

        await ctx.send(msg)

    async def incr(self, guild_id, user_id, user_name, amount):
        if not await self.is_enabled(guild_id):
            return
        await self.score_repo.upsert_or_increment_point(guild_id, user_id, user_name, amount)

async def setup(bot):
    await bot.add_cog(ScoreCog(bot))
