import discord
import asyncio
from core.bot import bot, CHANNEL_NOI_TU_ID
from typing import Set
from datetime import datetime
from apps.score import incr

# Lazy load repository để tránh lỗi database connection
noi_tu_repo = None

def get_noi_tu_repo():
    """Lazy load repository"""
    global noi_tu_repo
    if noi_tu_repo is None:
        from repositories.noi_tu import NoiTuRepository
        noi_tu_repo = NoiTuRepository()
    return noi_tu_repo

# Game state
class NoiTuGame:
    def __init__(self):
        self.is_active = False
        self.current_word = ""
        self.used_words: Set[str] = set()
        self.last_player_id = None
        self.last_player_name = None  # Thêm tên người chơi cuối
        self.last_message_time = None
        self.timeout_task = None
        self.channel = None
        self.timer_message = None  # Tin nhắn hiển thị thời gian
        self.timer_task = None     # Task cập nhật thời gian
        self.start_time = None     # Thời gian bắt đầu game
        self.lock = asyncio.Lock()

# Khởi tạo game state
game = NoiTuGame()

def is_admin(ctx):
    """Kiểm tra xem user có phải là admin không"""
    return ctx.author.guild_permissions.administrator

def is_correct_channel(ctx):
    """Kiểm tra xem command có được thực hiện trong đúng channel không"""
    return ctx.channel.id == CHANNEL_NOI_TU_ID

def get_first_word(word: str) -> str:
    return word.strip().split()[0] if word else ''

def get_last_word(word: str) -> str:
    return word.strip().split()[-1] if word else ''

def is_valid(prev, next: str) -> bool:
    return get_last_word(prev) == get_first_word(next)

def format_time_remaining(seconds: int) -> str:
    """Format thời gian còn lại"""
    if seconds <= 0:
        return "⏰ Hết thời gian!"
    return f"⏰ Còn lại: {seconds} giây"

async def update_timer_message():
    """Cập nhật tin nhắn thời gian mỗi 1 giây"""
    start_time = game.last_message_time
    if not start_time:
        return
        
    for remaining in range(30, -1, -1):  # Đếm ngược từ 30 đến 0
        if not game.is_active or not game.timer_message:
            break
            
        try:
            # Cập nhật embed
            embed = game.timer_message.embeds[0]
            embed.title = format_time_remaining(remaining)
            
            # Thay đổi màu sắc theo thời gian
            if remaining <= 5:
                embed.color = discord.Color.red()
            elif remaining <= 10:
                embed.color = discord.Color.orange()
            elif remaining <= 20:
                embed.color = discord.Color.yellow()
            else:
                embed.color = discord.Color.blue()
            
            await game.timer_message.edit(embed=embed)
            
            # Dừng nếu hết thời gian
            if remaining <= 0:
                break
                
            await asyncio.sleep(1)  # Đợi đúng 1 giây
            
        except Exception as e:
            print(f"Error updating timer: {e}")
            break

@bot.command(name='start')
async def start_game(ctx):
    """Bắt đầu trò chơi nối từ"""
    if not is_correct_channel(ctx):
        return
    
    if game.is_active:
        await ctx.send("❌ Trò chơi đã đang diễn ra!")
        return
    
    # Lấy repository
    repo = get_noi_tu_repo()
    
    # Lấy từ ngẫu nhiên để bắt đầu
    start_word = await repo.get_random_word()
    if not start_word:
        await ctx.send("❌ Không có từ nào trong cơ sở dữ liệu!")
        return
    
    # Khởi tạo game
    game.is_active = True
    game.current_word = start_word
    game.used_words = {start_word}
    game.last_player_id = None
    game.last_player_name = None
    game.channel = ctx.channel
    game.last_message_time = datetime.now()
    game.start_time = datetime.now()
    
    # Tạo timeout task
    game.timeout_task = asyncio.create_task(game_timeout())
    
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

@bot.command(name='end')
async def end_game(ctx):
    """Kết thúc trò chơi nối từ"""
    if not is_correct_channel(ctx):
        return
    
    if not game.is_active:
        await ctx.send("❌ Không có trò chơi nào đang diễn ra!")
        return
    
    # Dừng các task
    if game.timeout_task:
        game.timeout_task.cancel()
    if game.timer_task:
        game.timer_task.cancel()
    
    # Tính thời gian chơi
    game_duration = ""
    if game.start_time:
        duration = datetime.now() - game.start_time
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        game_duration = f"{minutes} phút {seconds} giây"
    
    # Tạo thông báo kết thúc
    embed = discord.Embed(
        title="🏁 Trò chơi Nối Từ đã kết thúc!",
        description=f"📊 **Thống kê:**\n"
                   f"• Số từ đã sử dụng: {len(game.used_words)}\n"
                   f"• Từ cuối cùng: {game.current_word if game.current_word else 'N/A'}\n"
                   f"• Thời gian chơi: {game_duration}",
        color=discord.Color.red()
    )
    
    # Thêm thông tin người chiến thắng
    if game.last_player_name:
        embed.add_field(
            name="👑 Người chiến thắng",
            value=f"**{game.last_player_name}** - Từ cuối: **{game.current_word}**",
            inline=False
        )
    
    await ctx.send(embed=embed)
    
    # Reset game state
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

@bot.command(name='add')
async def add_word(ctx, *, word: str):
    """Thêm từ mới vào cơ sở dữ liệu (chỉ admin)"""
    if not is_correct_channel(ctx):
        return
    
    if not is_admin(ctx):
        await ctx.send("❌ Chỉ admin mới có thể thêm từ!")
        return
    
    # Kiểm tra từ có hợp lệ không
    if not await get_noi_tu_repo().is_valid_word(word):
        await ctx.send("❌ Từ phải có đúng 2 từ ghép!")
        return
    
    # Kiểm tra từ đã tồn tại chưa
    if await get_noi_tu_repo().is_exist(word):
        await ctx.send(f"❌ Từ '{word}' đã tồn tại trong cơ sở dữ liệu!")
        return
    
    # Thêm từ
    success = await get_noi_tu_repo().add(word)
    if success:
        embed = discord.Embed(
            title="✅ Thêm từ thành công!",
            description=f"Từ: **{word}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Có lỗi xảy ra khi thêm từ!")

@bot.command(name='remove')
async def remove_word(ctx, *, word: str):
    """Xóa từ khỏi cơ sở dữ liệu (chỉ admin)"""
    if not is_correct_channel(ctx):
        return
    
    if not is_admin(ctx):
        await ctx.send("❌ Chỉ admin mới có thể xóa từ!")
        return
    
    # Kiểm tra từ có tồn tại không
    if not await get_noi_tu_repo().is_exist(word):
        await ctx.send(f"❌ Từ '{word}' không tồn tại trong cơ sở dữ liệu!")
        return
    
    # Xóa từ
    success = await get_noi_tu_repo().remove(word)
    if success:
        embed = discord.Embed(
            title="✅ Xóa từ thành công!",
            description=f"Đã xóa từ: **{word}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Có lỗi xảy ra khi xóa từ!")

async def game_timeout():
    """Xử lý timeout của game"""
    try:
        # Đợi đúng 30 giây
        for i in range(30):
            if not game.is_active:
                return
            await asyncio.sleep(1)
        
        # Kiểm tra lại trước khi timeout
        if game.is_active and game.last_message_time:
            time_diff = datetime.now() - game.last_message_time
            if time_diff.total_seconds() >= 30:
                # Game timeout
                embed = discord.Embed(
                    title="⏰ Hết thời gian!",
                    description=f"Không ai trả lời trong 30 giây.\n"
                               f"Từ cuối cùng: **{game.current_word}**\n"
                               f"Trò chơi kết thúc!",
                    color=discord.Color.orange()
                )
                
                # Thêm thông tin người chiến thắng
                if game.last_player_name:
                    embed.add_field(
                        name="👑 Người chiến thắng",
                        value=f"**{game.last_player_name}** - Từ cuối: **{game.current_word}**",
                        inline=False
                    )
                    if len(game.used_words) > 2:
                        await incr(game.last_player_id, game.last_player_name, 1)
                
                if game.channel:
                    await game.channel.send(embed=embed)
                
                # Reset game
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
                
    except asyncio.CancelledError:
        pass

@bot.listen('on_message')
async def handle_game_message(message):
    """Xử lý tin nhắn trong game"""
    # Bỏ qua tin nhắn từ bot
    if message.author.bot:
        return
    
    # Chỉ xử lý trong channel được chỉ định
    if message.channel.id != CHANNEL_NOI_TU_ID:
        return
    
    # Nếu game không active, bỏ qua
    if not game.is_active:
        return
    
    # Kiểm tra xem tin nhắn có phải là từ không
    word = message.content.strip().lower()
    if len(word.split()) != 2:
        return
    
    # Kiểm tra từ có hợp lệ không
    if not await get_noi_tu_repo().is_valid_word(word):
        return
    
    # Kiểm tra người vừa trả lời có trả lời tiếp không
    if game.last_player_id == message.author.id:
        # ignore
        # await message.add_reaction('❌')
        # await message.channel.send(f"❌ **{message.author.display_name}**, hãy để người khác trả lời!")
        return
    
    
    # Kiểm tra từ đã được sử dụng chưa
    if word in game.used_words:
        await message.add_reaction('❌')
        await message.channel.send(f"❌ Từ '{word}' đã được sử dụng!")
        return
    
    # Kiểm tra quy tắc nối từ ghép
    if game.current_word:
        if not is_valid(game.current_word, word):
            return

    # Kiểm tra từ có tồn tại trong DB không
    if not await get_noi_tu_repo().is_exist(word):
        await message.add_reaction('❌')
        return

    async with game.lock:
        if not is_valid(game.current_word, word):
            return
        # Từ hợp lệ
        await message.add_reaction('✅')
        
        # Cập nhật game state
        game.current_word = word
        game.used_words.add(word)
        game.last_player_id = message.author.id
        game.last_player_name = message.author.display_name  # Lưu tên người chơi
        game.last_message_time = datetime.now()
        
        # Reset timeout
        if game.timeout_task:
            game.timeout_task.cancel()
        game.timeout_task = asyncio.create_task(game_timeout())
        
        # Dừng timer task cũ nếu có
        if game.timer_task:
            game.timer_task.cancel()
        
        # Thông báo từ tiếp theo
        next_hint = get_last_word(word).upper()
        embed = discord.Embed(
            title="⏰ Còn lại: 30 giây",
            color=discord.Color.blue()
        )
        
        # Gửi tin nhắn mới và lưu reference
        game.timer_message = await message.channel.send(embed=embed)
        
        # Bắt đầu task cập nhật thời gian
        game.timer_task = asyncio.create_task(update_timer_message())

