import discord
from discord.ext import commands
from repositories import HomeDebtRepository
from repositories.config import ConfigRepository
from repositories.feature_toggle import FeatureToggleRepository
from utils.common import format_vnd

class HomeDebtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.home_debt_repo = HomeDebtRepository()
        self.config_repo = ConfigRepository()
        self.feature_repo = FeatureToggleRepository()

    async def get_allowed_channel_ids(self, guild_id: int) -> list[int]:
        config_value = await self.config_repo.get(guild_id, "CHANNEL_HOME_DEBT_ID", "")
        ids = []
        if config_value:
            for x in config_value.split(','):
                try:
                    ids.append(int(x.strip()))
                except ValueError:
                    pass
        return ids

    async def is_enabled(self, guild_id: int) -> bool:
        return await self.feature_repo.get(guild_id, "home_debt")

    async def is_correct_channel(self, ctx):
        """Kiểm tra xem command có được thực hiện trong đúng channel không"""
        if not await self.is_enabled(ctx.guild.id):
            return False

        allowed_ids = await self.get_allowed_channel_ids(ctx.guild.id)
        
        # New Rule: If no channels configured, allow ALL channels
        if not allowed_ids:
            return True
            
        return ctx.channel.id in allowed_ids

    @commands.command(name="hdadd", description="Thêm khoản chi tiêu mới")
    async def add(self, ctx, amount: int):
        """Vì home chỉ có 2 người nên sẽ tự động thêm khoản chi tiêu cho người còn lại"""
        try:
            if not await self.is_correct_channel(ctx):
                return
            
            # Get info other user from home_debt table for THIS GUILD
            other_user = await self.home_debt_repo.get_other(ctx.guild.id, ctx.author.id)
            if not other_user:
                await ctx.send("Không tìm thấy người dùng còn lại trong Guild này!")
                return

            other_user.value += round(amount / 2)
            resp = await self.home_debt_repo.update_home_debt(other_user)
            if not resp:
                await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu")
                return
            
            await ctx.send(f"Đã thêm {format_vnd(round(amount * 1000 / 2))} cho {ctx.author.name}. Số dư hiện tại là {format_vnd(other_user.value * 1000)}")
        except Exception as e:
            await ctx.send(f"Có lỗi xảy ra: {str(e)}")

    @commands.command(name="hdcheck", description="Kiểm tra số dư của bạn")
    async def home_debt_check(self, ctx):
        """Kiểm tra số dư của mọi người"""
        try:
            if not await self.is_correct_channel(ctx):
                return
            
            # Get info user from home_debt table for THIS GUILD
            users = await self.home_debt_repo.get_all(ctx.guild.id)
            embed = discord.Embed(title=f"Số dư của mọi người tại {ctx.guild.name}", color=discord.Color.blue())
            for user in users:
                value = format_vnd(user.value * 1000)
                member = ctx.guild.get_member(user.user_id)
                name = member.display_name if member else f"User {user.user_id}"
                embed.add_field(name=name, value=f"{value}", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Có lỗi xảy ra: {str(e)}")

    @commands.command(name="hdvay", description="Vay nợ")
    async def vay(self, ctx, amount: int):
        """Vay nợ"""
        try:
            if not await self.is_correct_channel(ctx):
                return
            
            # Get info user from home_debt table for THIS GUILD
            user = await self.home_debt_repo.get(ctx.guild.id, ctx.author.id)
            if not user:
                 user = await self.home_debt_repo.create_home_debt(ctx.guild.id, ctx.author.id, 0)

            user.value += amount
            resp = await self.home_debt_repo.update_home_debt(user)
            if not resp:
                await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu")
                return
            
            # Send message to user
            await ctx.send(f"Đã vay {format_vnd(amount * 1000)} bởi {ctx.author.name}")
        except Exception as e:
            await ctx.send(f"Có lỗi xảy ra: {str(e)}")

    @commands.command(name="hdtra", description="Trả nợ")
    async def tra(self, ctx, amount: int):
        """Trả nợ"""
        try:
            if not await self.is_correct_channel(ctx):
                return
            
            # Get info user from home_debt table for THIS GUILD
            user = await self.home_debt_repo.get(ctx.guild.id, ctx.author.id)
            if not user:
                 user = await self.home_debt_repo.create_home_debt(ctx.guild.id, ctx.author.id, 0)

            user.value -= amount
            resp = await self.home_debt_repo.update_home_debt(user)
            if not resp:
                await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu")
                return
            
            # Send message to user
            await ctx.send(f"Đã trả {format_vnd(amount * 1000)} từ {ctx.author.name}")
        except Exception as e:
            await ctx.send(f"Có lỗi xảy ra: {str(e)}")

async def setup(bot):
    await bot.add_cog(HomeDebtCog(bot))