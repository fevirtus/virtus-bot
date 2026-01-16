import discord
import asyncio
from discord.ext import commands
from typing import Set, Dict, List, Optional
from datetime import datetime

from repositories.noi_tu import NoiTuRepository
from repositories.score import ScoreRepository
from repositories.config import ConfigRepository
from repositories.feature_toggle import FeatureToggleRepository

# Game state class
class NoiTuGame:
    def __init__(self):
        self.is_active = False
        self.current_word = ""
        self.used_words: Set[str] = set()
        self.last_player_id = None
        self.last_player_name = None
        self.last_message_time = None
        self.timeout_task = None
        self.channel = None
        self.timer_message = None
        self.timer_task = None
        self.start_time = None
        self.lock = asyncio.Lock()

class NoiTuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.noi_tu_repo = NoiTuRepository()
        self.score_repo = ScoreRepository()
        self.config_repo = ConfigRepository()
        self.feature_repo = FeatureToggleRepository()
        self.games: Dict[int, NoiTuGame] = {}

    def get_game_for_channel(self, channel_id: int) -> NoiTuGame:
        if channel_id not in self.games:
            self.games[channel_id] = NoiTuGame()
        return self.games[channel_id]

    async def is_enabled(self, guild_id: int) -> bool:
        return await self.feature_repo.get(guild_id, "noi_tu")

    async def get_allowed_channel_ids(self, guild_id: int) -> List[int]:
        config = await self.config_repo.get(guild_id, "CHANNEL_NOI_TU_IDS", "")
        ids = []
        if config:
            for x in config.split(','):
                try:
                    ids.append(int(x.strip()))
                except ValueError:
                    pass
        return ids

    async def get_admin_ids(self, guild_id: int) -> List[int]:
        config = await self.config_repo.get(guild_id, "ADMIN_IDS", "")
        ids = []
        if config:
            for x in config.split(','):
                try:
                    ids.append(int(x.strip()))
                except ValueError:
                    pass
        return ids

    async def is_correct_channel(self, ctx) -> bool:
        if not await self.is_enabled(ctx.guild.id):
            return False

        allowed_ids = await self.get_allowed_channel_ids(ctx.guild.id)
        
        # New Rule: If no channels configured, allow ALL channels
        if not allowed_ids:
            return True
            
        return ctx.channel.id in allowed_ids

    async def is_admin(self, ctx) -> bool:
        admin_ids = await self.get_admin_ids(ctx.guild.id)
        return ctx.author.id in admin_ids

    # Helper functions
    def get_first_word(self, word: str) -> str:
        return word.strip().split()[0] if word else ''

    def get_last_word(self, word: str) -> str:
        return word.strip().split()[-1] if word else ''

    def is_valid(self, prev, next: str) -> bool:
        return self.get_last_word(prev) == self.get_first_word(next)

    def format_time_remaining(self, seconds: int) -> str:
        if seconds <= 0:
            return "⏰ Hết thời gian!"
        return f"⏰ Còn lại: {seconds} giây"

    async def update_timer_message(self, game: NoiTuGame):
        start_time = game.last_message_time
        if not start_time:
            return
            
        for remaining in range(30, -1, -1):
            if not game.is_active or not game.timer_message:
                break
                
            try:
                if len(game.timer_message.embeds) == 0:
                    break

                embed = game.timer_message.embeds[0]
                embed.title = self.format_time_remaining(remaining)
                
                if remaining <= 5:
                    embed.color = discord.Color.red()
                elif remaining <= 10:
                    embed.color = discord.Color.orange()
                elif remaining <= 20:
                    embed.color = discord.Color.yellow()
                else:
                    embed.color = discord.Color.blue()
                
                await game.timer_message.edit(embed=embed)
                
                if remaining <= 0:
                    break
                    
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error updating timer: {e}")
                break

    async def game_timeout(self, game: NoiTuGame):
        try:
            for i in range(30):
                if not game.is_active:
                    return
                await asyncio.sleep(1)
            
            if game.is_active and game.last_message_time:
                time_diff = datetime.now() - game.last_message_time
                if time_diff.total_seconds() >= 30:
                    embed = discord.Embed(
                        title="⏰ Hết thời gian!",
                        description=f"Không ai trả lời trong 30 giây.\n"
                                   f"Từ cuối cùng: **{game.current_word}**\n"
                                   f"Trò chơi kết thúc!",
                        color=discord.Color.orange()
                    )
                    
                    if game.last_player_name:
                        embed.add_field(
                            name="👑 Người chiến thắng",
                            value=f"**{game.last_player_name}** - Từ cuối: **{game.current_word}**",
                            inline=False
                        )
                        if len(game.used_words) > 2 and game.channel and game.channel.guild:
                            # Update score for the guild
                            await self.score_repo.upsert_or_increment_point(game.channel.guild.id, game.last_player_id, game.last_player_name, 1)
                    
                    if game.channel:
                        await game.channel.send(embed=embed)
                    
                    self.reset_game(game)
                    
        except asyncio.CancelledError:
            pass

    def reset_game(self, game: NoiTuGame):
        game.is_active = False
        game.current_word = ""
        game.used_words.clear()
        game.last_player_id = None
        game.last_player_name = None
        game.channel = None
        game.last_message_time = None
        game.timeout_task = None
        game.timer_message = None
        game.timer_task = None
        game.start_time = None

    @commands.command(name='start')
    async def start_game(self, ctx):
        if not await self.is_correct_channel(ctx):
            return
        
        game = self.get_game_for_channel(ctx.channel.id)
        
        if game.is_active:
            await ctx.send("❌ Trò chơi đã đang diễn ra!")
            return
        
        start_word = await self.noi_tu_repo.get_random_word()
        if not start_word:
            await ctx.send("❌ Không có từ nào trong cơ sở dữ liệu!")
            return
        
        game.is_active = True
        game.current_word = start_word
        game.used_words = {start_word}
        game.last_player_id = None
        game.last_player_name = None
        game.channel = ctx.channel
        game.last_message_time = datetime.now()
        game.start_time = datetime.now()
        
        game.timeout_task = asyncio.create_task(self.game_timeout(game))
        
        embed = discord.Embed(
            title="🎮 Trò chơi Nối Từ đã bắt đầu!",
            description=f"Từ đầu tiên: **{start_word}**\n\n"
                       f"📝 **Luật chơi:**\n"
                       f"• Mỗi từ gồm 2 từ ghép tiếng Việt (VD: 'âm cao', 'cao độ')\n"
                       f"• Từ đầu của từ mới phải trùng với từ cuối của từ trước\n"
                       f"• Không được lặp lại từ đã dùng\n"
                       f"• Thời gian trả lời tối đa: 30 giây\n\n"
                       f"⏰ Thời gian bắt đầu: {datetime.now().strftime('%H:%M:%S')}",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='end')
    async def end_game(self, ctx):
        if not await self.is_correct_channel(ctx):
            return
        
        game = self.get_game_for_channel(ctx.channel.id)
        
        if not game.is_active:
            await ctx.send("❌ Không có trò chơi nào đang diễn ra!")
            return
        
        if game.timeout_task:
            game.timeout_task.cancel()
        if game.timer_task:
            game.timer_task.cancel()
        
        game_duration = ""
        if game.start_time:
            duration = datetime.now() - game.start_time
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            game_duration = f"{minutes} phút {seconds} giây"
        
        embed = discord.Embed(
            title="🏁 Trò chơi Nối Từ đã kết thúc!",
            description=f"📊 **Thống kê:**\n"
                       f"• Số từ đã sử dụng: {len(game.used_words)}\n"
                       f"• Từ cuối cùng: {game.current_word if game.current_word else 'N/A'}\n"
                       f"• Thời gian chơi: {game_duration}",
            color=discord.Color.red()
        )
        
        if game.last_player_name:
            embed.add_field(
                name="👑 Người chiến thắng",
                value=f"**{game.last_player_name}** - Từ cuối: **{game.current_word}**",
                inline=False
            )
        
        await ctx.send(embed=embed)
        self.reset_game(game)

    @commands.command(name='add')
    async def add_word(self, ctx, *, word: str):
        if not await self.is_correct_channel(ctx):
            return
        
        if not await self.is_admin(ctx):
            await ctx.send("❌ Chỉ admin mới có thể thêm từ!")
            return
        
        if not await self.noi_tu_repo.is_valid_word(word):
            await ctx.send("❌ Từ phải có đúng 2 từ ghép!")
            return
        
        success = await self.noi_tu_repo.add(word)
        if success:
            embed = discord.Embed(
                title="✅ Thêm từ thành công!",
                description=f"Từ: **{word}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            if await self.noi_tu_repo.is_exist(word):
                await ctx.send(f"❌ Từ '{word}' đã tồn tại trong cơ sở dữ liệu!")
            else:
                await ctx.send("❌ Có lỗi xảy ra khi thêm từ!")

    @commands.command(name='remove')
    async def remove_word(self, ctx, *, word: str):
        if not await self.is_correct_channel(ctx):
            return
        
        if not await self.is_admin(ctx):
            await ctx.send("❌ Chỉ admin mới có thể xóa từ!")
            return
        
        if not await self.noi_tu_repo.is_exist(word):
            await ctx.send(f"❌ Từ '{word}' không tồn tại trong cơ sở dữ liệu!")
            return
        
        success = await self.noi_tu_repo.remove(word)
        if success:
            embed = discord.Embed(
                title="✅ Xóa từ thành công!",
                description=f"Đã xóa từ: **{word}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Có lỗi xảy ra khi xóa từ!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        # Check if enabled for this guild
        if not await self.is_enabled(message.guild.id):
            return
            
        # Check channel
        allowed_ids = await self.get_allowed_channel_ids(message.guild.id)
        if message.channel.id not in allowed_ids:
            return
        
        game = self.get_game_for_channel(message.channel.id)
        
        if not game.is_active:
            return
        
        word = message.content.strip().lower()
        if len(word.split()) != 2:
            return
        
        if not await self.noi_tu_repo.is_valid_word(word):
            return
        
        if game.last_player_id == message.author.id:
            return
        
        if word in game.used_words:
            await message.add_reaction('❌')
            await message.channel.send(f"❌ Từ '{word}' đã được sử dụng!")
            return
        
        if game.current_word:
            if not self.is_valid(game.current_word, word):
                return

        if not await self.noi_tu_repo.is_exist(word):
            await message.add_reaction('❌')
            return

        async with game.lock:
            if not self.is_valid(game.current_word, word):
                return
            
            await message.add_reaction('✅')
            
            game.current_word = word
            game.used_words.add(word)
            game.last_player_id = message.author.id
            game.last_player_name = message.author.display_name
            game.last_message_time = datetime.now()
            
            if game.timeout_task:
                game.timeout_task.cancel()
            game.timeout_task = asyncio.create_task(self.game_timeout(game))
            
            if game.timer_task:
                game.timer_task.cancel()
            
            next_hint = self.get_last_word(word).upper()
            embed = discord.Embed(
                title="⏰ Còn lại: 30 giây",
                color=discord.Color.blue()
            )
            
            game.timer_message = await message.channel.send(embed=embed)
            game.timer_task = asyncio.create_task(self.update_timer_message(game))

async def setup(bot):
    await bot.add_cog(NoiTuCog(bot))
