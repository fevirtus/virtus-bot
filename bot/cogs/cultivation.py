"""Discord adapter. All economic changes go through the transactional game store."""
import asyncio
import logging
import time
from typing import Union, Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

from infra.db import postgres
from services.cultivation import engine as E, rules as R
from services.cultivation.bootstrap import provision, SetupError
from services.cultivation.store import GameStore

log = logging.getLogger(__name__)


def eligible_voice(guild, ignored=()):
    result = {}
    for channel in guild.voice_channels + guild.stage_channels:
        if channel == guild.afk_channel or getattr(channel, 'id', None) in ignored:
            continue
        members = [m for m in channel.members if not m.bot and m.voice and
                   not m.voice.self_deaf and not m.voice.deaf and not m.voice.afk and
                   not getattr(m.voice, 'suppress', False)]
        if len(members) >= 2:
            result.update({m.id: m for m in members})
    return result


def profile_text(state, uid):
    p = state['players'][str(uid)]
    g = p['genetics']
    lines = [f"**{R.realm_name(p)} · tầng {p['tier']+1}** — {p['xp']:g}/{R.cap(p)} tu vi",
             f"Linh thạch: **{p['coins']}** · Chiến thuật: {p['strategy']} · Đan mang theo: {p['potions']}",
             f"Linh căn {g['root']} · {', '.join(g['talents'])}",
             f"Chỉ số: {g['stats']} · Cơ duyên {g['fortune']} · Kiếp số {g['calamity']}"]
    if p['candidate']:
        lines.append(f"**Bộ roll mới:** {p['candidate']}")
    if p['injury_until'] > time.time():
        lines.append(f"Trọng thương đến <t:{int(p['injury_until'])}:R>.")
    for job in state['jobs'].values():
        if str(uid) in job['users']:
            lines.append(f"{job['kind']}: hoàn tất <t:{int(job['due'])}:R>.")
            e = job.get('encounter')
            if e and e['owner'] == str(uid) and not e['choice'] and e['expires'] > time.time():
                lines.append(f"Dấu tích phó bản: mở <t:{int(e['opens'])}:R>, hết hạn <t:{int(e['expires'])}:R>; bỏ qua tự động nếu không chọn.")
    if p['event']:
        lines.append('**Gặp dấu tích bí ẩn.** Chọn quan sát, mở hoặc rời đi trong mục Kỳ ngộ.')
    lines.extend(x['text'] for x in p['inbox'][-2:])
    return '\n'.join(lines)[:3900]


class OwnedView(discord.ui.View):
    def __init__(self, cog, uid, timeout=300):
        super().__init__(timeout=timeout)
        self.cog, self.uid = cog, uid

    async def interaction_check(self, interaction):
        if interaction.user.id != self.uid:
            await interaction.response.send_message('Hãy mở hồ sơ của chính bạn.', ephemeral=True)
            return False
        return True

    async def on_error(self, interaction, error, item):
        log.exception('Cultivation UI error', exc_info=error)
        if interaction.response.is_done():
            await interaction.followup.send('Thao tác chưa hoàn tất; thử lại bằng bảng điều khiển mới.', ephemeral=True)
        else:
            await interaction.response.send_message('Thao tác chưa hoàn tất; thử lại bằng bảng điều khiển mới.', ephemeral=True)


class Confirm(OwnedView):
    def __init__(self, cog, uid, op, args, quoted):
        super().__init__(cog, uid, 120)
        self.op, self.args, self.quoted = op, args, quoted
        self.done = False

    @discord.ui.button(label='Xác nhận', style=discord.ButtonStyle.success)
    async def confirm(self, interaction, button):
        if self.done:
            await interaction.response.send_message('Thao tác này đã được gửi.', ephemeral=True)
            return
        self.done = True
        await interaction.response.defer(ephemeral=True)
        try:
            if self.op == 'upgrade' and interaction.user.id != interaction.guild.owner_id:
                raise E.GameError('Chỉ chủ server hiện tại được nâng cấp.')
            text = await self.cog.store.act(interaction.guild_id, self.uid, interaction.user.display_name,
                                            interaction.message.id, self.op,
                                            dict(self.args, _quote=self.quoted))
            if self.op == 'roll':
                state, _ = await self.cog.store.snapshot(interaction.guild_id)
                text += '\n'+profile_text(state, self.uid)
            await interaction.edit_original_response(content=None, embed=discord.Embed(description=text[:3900], color=0x477b65), view=Personal(self.cog, self.uid))
            await self.cog.sync_roles(interaction.guild)
        except E.GameError as error:
            await interaction.edit_original_response(content=str(error), view=None)

    @discord.ui.button(label='Hủy', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, button):
        self.done = True
        await interaction.response.edit_message(content='Đã hủy, chưa chi vật phẩm.', view=None)


class Pages(OwnedView):
    def __init__(self, cog, uid, pages):
        super().__init__(cog, uid)
        self.pages, self.index = pages or ['Chưa có dữ liệu.'], 0

    def text(self):
        return f"Trang {self.index+1}/{len(self.pages)}\n"+self.pages[self.index]

    @discord.ui.button(label='Trước')
    async def previous(self, interaction, button):
        self.index = (self.index-1) % len(self.pages)
        await interaction.response.edit_message(content=self.text(), view=self)

    @discord.ui.button(label='Tiếp')
    async def next_page(self, interaction, button):
        self.index = (self.index+1) % len(self.pages)
        await interaction.response.edit_message(content=self.text(), view=self)

    @discord.ui.button(label='Hồ sơ')
    async def home(self, interaction, button):
        await self.cog.action(interaction, 'show', {}, False)


def paginate(lines, limit=1750):
    pages, current = [], ''
    for line in lines:
        # A single unusually long entry is also split, never silently discarded.
        for start in range(0, max(1, len(line)), limit):
            part = line[start:start+limit]
            if current and len(current)+len(part)+1 > limit:
                pages.append(current)
                current = ''
            current += ('\n' if current else '')+part
    if current:
        pages.append(current)
    return pages or ['Chưa có dữ liệu.']


def inventory_lines(p, query='', realm=None, quality=None):
    lines = []
    for key, count in sorted(p['inventory'].items()):
        r, item, q = key.split(':')
        if not count or (realm is not None and int(r) != realm) or (quality and q != quality):
            continue
        if query.casefold() not in (R.NAMES.get(item, item)+' '+item).casefold():
            continue
        effect, source = R.ITEM_INFO.get(item, ('Vật phẩm đặc biệt', 'Hoạt động'))
        tradable = 'Được tặng' if item in R.TRADABLE else 'Khóa chuyển giao'
        lines.append(f"**{R.NAMES.get(item, item)} ×{count}** · {R.REALMS[int(r)]} · {'Thượng phẩm' if q == 'fine' else 'Đạt chuẩn'}\n{effect} · {source} · {tradable}")
    return lines


class BagSearch(discord.ui.Modal, title='Tìm trong túi'):
    query = discord.ui.TextInput(label='Tên vật phẩm', required=False, max_length=80)

    def __init__(self, view):
        super().__init__()
        self.parent = view

    async def on_submit(self, interaction):
        if interaction.user.id != self.parent.uid:
            await interaction.response.send_message('Đây không phải túi của bạn.', ephemeral=True)
            return
        self.parent.query = str(self.query)
        await self.parent.refresh(interaction)


class BagView(Pages):
    def __init__(self, cog, uid, p, query='', realm=None, quality=None):
        self.query, self.realm, self.quality = query, realm, quality
        super().__init__(cog, uid, paginate(inventory_lines(p, query, realm, quality)))
        select = discord.ui.Select(placeholder='Lọc cảnh giới', row=1, options=[discord.SelectOption(label='Mọi cảnh giới', value='all')]+
                                   [discord.SelectOption(label=n, value=str(i)) for i, n in enumerate(R.REALMS)])
        async def select_realm(interaction):
            self.realm = None if select.values[0] == 'all' else int(select.values[0])
            await self.refresh(interaction)
        select.callback = select_realm
        self.add_item(select)
        quality_select = discord.ui.Select(placeholder='Lọc chất lượng', row=2, options=[
            discord.SelectOption(label=n, value=v) for n, v in [('Mọi chất lượng','all'),('Đạt chuẩn','normal'),('Thượng phẩm','fine')]])
        async def select_quality(interaction):
            self.quality = None if quality_select.values[0] == 'all' else quality_select.values[0]
            await self.refresh(interaction)
        quality_select.callback = select_quality
        self.add_item(quality_select)

    async def refresh(self, interaction):
        await interaction.response.defer()
        state, _ = await self.cog.store.snapshot(interaction.guild_id)
        self.pages = paginate(inventory_lines(state['players'][str(self.uid)], self.query, self.realm, self.quality))
        self.index = 0
        await interaction.edit_original_response(content=self.text(), view=self)

    @discord.ui.button(label='Tìm kiếm', row=3)
    async def search(self, interaction, button):
        await interaction.response.send_modal(BagSearch(self))


class ActionSelect(discord.ui.Select):
    def __init__(self, cog, uid, actions, placeholder):
        self.cog, self.uid, self.actions = cog, uid, actions
        super().__init__(placeholder=placeholder, options=[discord.SelectOption(label=label, value=str(i))
                         for i, (label, op, args, confirm) in enumerate(actions)])

    async def callback(self, interaction):
        label, op, args, confirm = self.actions[int(self.values[0])]
        await self.cog.action(interaction, op, args, confirm)


class Personal(OwnedView):
    def __init__(self, cog, uid):
        super().__init__(cog, uid)
        self.add_item(ActionSelect(cog, uid, [
            ('Hồ sơ / cập nhật', 'show', {}, False), ('Túi đồ', 'bag', {}, False),
            ('Hộp thư', 'inbox', {}, False), ('Đột phá', 'breakthrough', {}, True),
            ('Đại đột phá + Hộ Mạch Đan', 'breakthrough', {'guard': True}, True),
            ('Roll tư chất', 'roll', {}, True), ('Nhận bộ mới', 'accept_roll', {}, False),
            ('Giữ bộ cũ', 'keep_roll', {}, False), ('Dưỡng thương', 'heal_injury', {}, True),
            ('Tông môn', 'sect', {}, False), ('Bảng xếp hạng', 'ranking', {}, False),
            ('Bật / ngừng tu luyện', 'toggle', {}, True),
            ('Bật / tắt thông báo DM', 'notifications', {}, False),
        ], 'Hồ sơ và tu luyện'))
        self.add_item(ActionSelect(cog, uid, [
            ('Thám hiểm · Linh thảo', 'explore', {'area': 'herb'}, False),
            ('Thám hiểm · Linh tuyền', 'explore', {'area': 'water'}, False),
            ('Thám hiểm · Tẩy tủy thảo', 'explore', {'area': 'marrow'}, False),
            ('Săn quái auto', 'hunt', {}, True), ('Phó bản cá nhân', 'dungeon', {}, True),
            ('Tạo đội phó bản', 'room_create', {}, False),
            ('Boss tông môn', 'sect_boss', {}, True),
            ('Nhận thưởng boss tuần', 'boss_claim', {}, False),
            ('Kỳ ngộ · quan sát', 'event', {'choice': 'inspect'}, True),
            ('Kỳ ngộ · mở', 'event', {'choice': 'open'}, True),
            ('Kỳ ngộ · rời đi', 'event', {'choice': 'leave'}, False),
            ('Dấu tích phó bản · quan sát', 'dungeon_event', {'choice': 'inspect'}, False),
            ('Dấu tích phó bản · mở', 'dungeon_event', {'choice': 'open'}, False),
            ('Dấu tích phó bản · bỏ qua', 'dungeon_event', {'choice': 'leave'}, False),
        ], 'Thám hiểm và chiến đấu'))
        self.add_item(ActionSelect(cog, uid, [(f'Luyện {R.NAMES[item]}', 'craft', {'item': item, 'count': 1}, True)
                                             for item in R.RECIPES] + [
            ('Mua 5 Linh thảo', 'buy', {'item': 'herb', 'count': 5}, True),
            ('Mua 5 Linh tuyền', 'buy', {'item': 'water', 'count': 5}, True),
            ('Hiến 5 Linh thảo', 'donate', {'count': 5}, True),
            ('Nhận dược viên', 'garden', {}, False),
            ('Nghiên cứu tàng kinh', 'library', {}, False),
            ('Học Ngưng Thần Đan', 'learn', {'item': 'focus'}, True),
            ('Dùng Ngưng Thần Đan', 'focus', {}, True),
            ('Nhận nhiệm vụ tuần', 'weekly', {}, False),
        ], 'Luyện đan và cửa hàng'))
        self.add_item(ActionSelect(cog, uid, [
            (f'Chiến thuật · {label}', 'strategy', {'value': value}, False)
            for label, value in [('Tấn công', 'attack'), ('Cân bằng', 'balanced'), ('Thận trọng', 'careful')]
        ] + [(f'Mang tối đa {n} đan / trận', 'potions', {'value': n}, False) for n in (0, 1, 2)] + [
            (f'Hướng tu · {label}', 'path', {'value': value}, True)
            for label, value in [('Kiếm tu', 'sword'), ('Thể tu', 'body'), ('Pháp tu', 'mage')]
        ], 'Cài đặt chiến đấu'))


class Panel(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label='Mở tu tiên', custom_id='virtus:open', style=discord.ButtonStyle.primary)
    async def open(self, interaction, button):
        await self.cog.action(interaction, 'show', {}, False)


class SectBoard(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label='Tham chiến boss', custom_id='virtus:boss', style=discord.ButtonStyle.primary)
    async def fight(self, interaction, button):
        await self.cog.action(interaction, 'sect_boss', {}, True)

    @discord.ui.button(label='Nhận thưởng boss', custom_id='virtus:boss_claim')
    async def claim(self, interaction, button):
        await self.cog.action(interaction, 'boss_claim', {}, False)

    @discord.ui.button(label='Nhiệm vụ tuần', custom_id='virtus:weekly')
    async def weekly(self, interaction, button):
        await self.cog.action(interaction, 'weekly', {}, False)


class Lobby(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    async def act(self, interaction, op):
        await interaction.response.defer(ephemeral=True)
        state, _ = await self.cog.store.snapshot(interaction.guild_id)
        rid = next((rid for rid, room in state['rooms'].items()
                    if room['message_id'] == interaction.message.id), None)
        if rid is None:
            await interaction.followup.send('Đội đã hết hạn hoặc xuất phát.', ephemeral=True)
            return
        try:
            text = await self.cog.store.act(interaction.guild_id, interaction.user.id,
                    interaction.user.display_name, interaction.id, op, {'room': rid})
            state, _ = await self.cog.store.snapshot(interaction.guild_id)
            room = state['rooms'].get(rid)
            content = 'Đội đã xuất phát hoặc kết thúc.'
            if room:
                content = 'Đội phó bản — ' + ', '.join(
                    f"{state['players'][u]['name']} {'✓' if u in room['ready'] else '…'}" for u in room['members'])
                content += '\nSẵn sàng chấp thuận ngân sách đan đã lưu và chủ đội chọn kỳ ngộ (chỉ ảnh hưởng linh thạch chặng boss). Hết lượt vẫn hỗ trợ, không thưởng.'
            await interaction.message.edit(content=content, view=Lobby(self.cog) if room else None,
                                           allowed_mentions=discord.AllowedMentions.none())
            await interaction.followup.send(text, ephemeral=True)
        except E.GameError as error:
            await interaction.followup.send(str(error), ephemeral=True)

    @discord.ui.button(label='Tham gia', custom_id='virtus:join')
    async def join(self, interaction, button):
        await self.act(interaction, 'room_join')

    @discord.ui.button(label='Sẵn sàng', custom_id='virtus:ready', style=discord.ButtonStyle.success)
    async def ready(self, interaction, button):
        await self.act(interaction, 'room_ready')

    @discord.ui.button(label='Rời đội', custom_id='virtus:leave')
    async def leave(self, interaction, button):
        await self.act(interaction, 'room_leave')

    @discord.ui.button(label='Xuất phát', custom_id='virtus:start', style=discord.ButtonStyle.primary)
    async def start(self, interaction, button):
        await self.act(interaction, 'room_start')


class Cultivation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.store = GameStore(postgres.session_maker)
        self.voice_members = {}
        self.voice_last = {}
        self.voice_lock = asyncio.Lock()
        self.started = False
        self.ignored = {}
        self.board_cache = {}
        self.delivery_lock = asyncio.Lock()

    async def cog_load(self):
        self.bot.add_view(Panel(self))
        self.bot.add_view(Lobby(self))
        self.bot.add_view(SectBoard(self))

    async def cog_unload(self):
        self.tick.cancel()

    async def setup_guild(self, guild):
        try:
            resources = await provision(self.bot, guild, self.store, Panel(self))
            self.ignored[guild.id] = resources.get('ignored_channels', [])
        except Exception as error:
            log.exception('Cultivation setup failed for guild %s', guild.id)
            await self.store.resource(guild.id, 'status', f'needs_attention: {type(error).__name__}')

    @commands.Cog.listener()
    async def on_ready(self):
        # Reconnecting must not count disconnected voice time.
        async with self.voice_lock:
            self.voice_members = {g.id: eligible_voice(g, self.ignored.get(g.id, [])) for g in self.bot.guilds}
            self.voice_last = {g.id: time.monotonic() for g in self.bot.guilds}
        for guild in self.bot.guilds:
            await self.setup_guild(guild)
        if not self.tick.is_running():
            self.tick.start()

    @commands.Cog.listener()
    async def on_disconnect(self):
        async with self.voice_lock:
            self.voice_members.clear()
            self.voice_last.clear()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.setup_guild(guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot or message.webhook_id or not message.content.strip():
            return
        if message.content.startswith('!'):
            return
        try:
            await self.store.reward_chat(message.guild.id, message.author.id, message.author.display_name,
                                         message.id, message.content, channel_ids=(message.channel.id, getattr(message.channel, 'parent_id', None)))
        except Exception:
            log.exception('Chat XP failed')

    async def voice_flush(self, guild):
        async with self.voice_lock:
            now = time.monotonic()
            elapsed = max(0, min(30, now-self.voice_last.get(guild.id, now)))
            previous = self.voice_members.get(guild.id, {})
            self.voice_members[guild.id] = eligible_voice(guild, self.ignored.get(guild.id, []))
            self.voice_last[guild.id] = now
            # Unique interval boundary per member; database cursor clips overlap,
            # including reconnects and a second worker processing the same interval.
            end = time.time()
            for member in previous.values():
                await self.store.reward_voice(guild.id, member.id, member.display_name,
                                             f'{member.id}:{end:.6f}', elapsed, end=end)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.voice_flush(member.guild)

    async def sync_roles(self, guild):
        state, resources = await self.store.snapshot(guild.id)
        roles = {i: guild.get_role(resources.get(f'realm_role_{i}', 0)) for i in range(len(R.REALMS))}
        owned = {r for r in roles.values() if r}
        for uid, p in state['players'].items():
            member = guild.get_member(int(uid))
            if not member:
                continue
            wanted = roles.get(p['realm']) if p['active'] else None
            try:
                stale = [r for r in member.roles if r in owned and r != wanted]
                if stale:
                    await member.remove_roles(*stale, reason='Cultivation realm sync')
                if wanted and wanted not in member.roles:
                    await member.add_roles(wanted, reason='Cultivation realm sync')
            except discord.HTTPException:
                log.warning('Realm role sync failed guild=%s user=%s', guild.id, uid)

    async def deliver_notices(self, guild):
        async with self.delivery_lock:
            state, resources = await self.store.snapshot(guild.id)
            for key, event in await self.store.pending_notices(guild.id):
                if event['kind'] == 'private':
                    p = state['players'].get(event['user'], {})
                    member = guild.get_member(int(event['user']))
                    if not member or not p.get('notifications'):
                        await self.store.notice_done(guild.id, key)
                        continue
                    try:
                        channel = await member.create_dm()
                    except discord.Forbidden:
                        await self.store.notice_done(guild.id, key)
                        continue
                else:
                    channel = guild.get_channel(resources.get('achievement_channel', 0))
                if not channel:
                    continue
                marker = f'virtus:{guild.id}:{key}'
                try:
                    found = False
                    async for old in channel.history(limit=50):
                        if old.author.id == self.bot.user.id and any(e.footer.text == marker for e in old.embeds):
                            found = True
                            break
                    if not found:
                        name = state['players'].get(event['user'], {}).get('name', 'Đạo hữu')
                        embed = discord.Embed(title='Thành tựu tu tiên' if event['kind'] == 'achievement' else 'Kết quả hoạt động',
                                              description=discord.utils.escape_markdown(name)+'\n'+event['text'][:3600], color=0x477b65)
                        embed.set_footer(text=marker)
                        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
                    await self.store.notice_done(guild.id, key)
                except discord.Forbidden:
                    # The durable in-game inbox remains the fallback when DMs are closed.
                    if event['kind'] == 'private':
                        await self.store.notice_done(guild.id, key)
                except discord.HTTPException:
                    log.warning('Notice delivery deferred guild=%s event=%s', guild.id, key)

    async def update_board(self, guild):
        state, resources = await self.store.snapshot(guild.id)
        channel = guild.get_channel(resources.get('sect_channel', 0))
        if not channel:
            return
        sect = state['sect']
        target = sect.get('boss_target') or 'chốt theo số đạo hữu khi bắt đầu'
        from datetime import datetime, timezone, timedelta
        end = datetime.fromisoformat(sect['week']).replace(tzinfo=timezone.utc)+timedelta(days=7, hours=-3)
        content = (f"**Tông môn · tuần {sect['week']}**\nBoss tuần: {sect['boss_damage']} / {target} sát thương. "
                   f"Mỗi người có 2 lượt đóng góp.\nNhiệm vụ: {sect['progress']}/100 cống hiến · Quỹ: {sect['fund']}\n"
                   f"Mở cả tuần; đặt lại <t:{int(end.timestamp())}:F>. Không cần chủ server mở sự kiện.")
        cached = self.board_cache.get(guild.id)
        if cached == (channel.id, content):
            return
        message = None
        if resources.get('board_channel') == channel.id and resources.get('board_message'):
            try:
                message = await channel.fetch_message(resources['board_message'])
            except discord.NotFound:
                pass
        if message is None:
            async for old in channel.history(limit=100):
                if old.author.id == self.bot.user.id and any(getattr(c, 'custom_id', '') == 'virtus:boss'
                                                           for row in old.components for c in row.children):
                    message = old
                    break
        if message:
            await message.edit(content=content, view=SectBoard(self), allowed_mentions=discord.AllowedMentions.none())
        else:
            message = await channel.send(content, view=SectBoard(self), allowed_mentions=discord.AllowedMentions.none())
        await self.store.resource(guild.id, 'board_message', message.id)
        await self.store.resource(guild.id, 'board_channel', channel.id)
        self.board_cache[guild.id] = (channel.id, content)

    @tasks.loop(seconds=30)
    async def tick(self):
        try:
            await self.store.settle_all()
            for guild in self.bot.guilds:
                await self.voice_flush(guild)
                try:
                    await self.sync_roles(guild)
                    await self.deliver_notices(guild)
                    await self.update_board(guild)
                except Exception:
                    log.exception('Guild delivery failed guild=%s; other guilds continue', guild.id)
        except Exception:
            log.exception('Cultivation recovery tick failed; retrying next tick')

    async def action(self, interaction, op, args, confirm):
        if not interaction.guild:
            await interaction.response.send_message('Dùng lệnh trong server.', ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            state, resources = await self.store.snapshot(interaction.guild_id, interaction.user.id, interaction.user.display_name)
            p = state['players'][str(interaction.user.id)]
            if confirm:
                quoted = E.quote(state, interaction.user.id, op, args)
                await interaction.followup.send(quoted, view=Confirm(self, interaction.user.id, op, args, quoted), ephemeral=True)
                return
            if op == 'show':
                text = profile_text(state, interaction.user.id)
            elif op == 'bag':
                view = BagView(self, interaction.user.id, p, args.get('query', ''), args.get('realm'), args.get('quality'))
                await interaction.followup.send(view.text(), view=view, ephemeral=True)
                return
            elif op == 'inbox':
                view = Pages(self, interaction.user.id, paginate([x['text'] for x in reversed(p['inbox'])]))
                await interaction.followup.send(view.text(), view=view, ephemeral=True)
                return
            elif op == 'sect':
                s = state['sect']
                text = f"Quỹ xây dựng: {s['fund']} · Cống hiến của bạn: {p['contribution']}\n" + '\n'.join(
                    f'{R.BUILDINGS[k]}: cấp {v}' for k, v in s['buildings'].items())
                text += f"\nNhiệm vụ tuần: {s['progress']}/100 · Boss: {s['boss_damage']}/{s.get('boss_target') or 'chốt khi xuất chiến'}"
                text += '\nDùng /tutien_bophieu để ưu tiên công trình. Chủ server dùng /tutien_nangcap.'
            elif op == 'ranking':
                lines = []
                for title, key in [('Cảnh giới', lambda pair: (pair[1]['realm'], pair[1]['tier'], pair[1]['xp'])),
                                   ('Cống hiến', lambda pair: pair[1]['contribution']),
                                   ('Hoạt động tuần', lambda pair: pair[1]['activity_points'].get(R.week_key(time.time()), 0))]:
                    lines.append('**'+title+'**')
                    lines.extend(f"{i}. {discord.utils.escape_markdown(p['name'])}" for i, (_, p) in
                                 enumerate(sorted(state['players'].items(), key=key, reverse=True)[:10], 1))
                text = '\n'.join(lines)
            else:
                text = await self.store.act(interaction.guild_id, interaction.user.id, interaction.user.display_name,
                                            interaction.id, op, args)
                if op == 'room_create':
                    channel = interaction.guild.get_channel(resources.get('game_channel', 0))
                    if channel is None:
                        raise E.GameError('Chưa có kênh tu tiên. Quản trị viên chạy /tutien_setup.')
                    rid = text
                    # A failed response/DB write after Discord send must not strand the owner.
                    marker = f'virtus:room:{rid}'
                    msg = None
                    async for old in channel.history(limit=100):
                        if old.author.id == self.bot.user.id and any(e.footer.text == marker for e in old.embeds):
                            msg = old
                            break
                    if msg is None:
                        embed = discord.Embed(description='Đội phó bản — tham gia rồi xác nhận chiến thuật/ngân sách đan. Chủ đội đại diện chọn kỳ ngộ; bỏ qua an toàn sau 60 giây. Chỉ linh thạch kiếm được ở chặng boss có thể bị ảnh hưởng, không tự lấy đồ riêng.')
                        embed.set_footer(text=marker)
                        msg = await channel.send(embed=embed, view=Lobby(self), allowed_mentions=discord.AllowedMentions.none())
                    await self.store.bind_room(interaction.guild_id, rid, msg.id)
                    text = f'Đã mở đội: {msg.jump_url}'
            await interaction.followup.send(embed=discord.Embed(description=text[:3900], color=0x477b65), view=Personal(self, interaction.user.id), ephemeral=True,
                                            allowed_mentions=discord.AllowedMentions.none())
        except E.GameError as error:
            await interaction.followup.send(str(error), ephemeral=True)

    @app_commands.command(name='tutien', description='Hồ sơ tu tiên, hoạt động auto và túi đồ')
    @app_commands.guild_only()
    async def tutien(self, interaction: discord.Interaction):
        await self.action(interaction, 'show', {}, False)

    @app_commands.command(name='tutien_luyen', description='Luyện một mẻ đan, xem chi phí trước khi xác nhận')
    @app_commands.guild_only()
    @app_commands.choices(item=[app_commands.Choice(name=R.NAMES[k], value=k) for k in R.RECIPES])
    async def craft(self, interaction: discord.Interaction, item: str, count: app_commands.Range[int, 1, 10] = 1):
        await self.action(interaction, 'craft', {'item': item, 'count': count}, True)

    @app_commands.command(name='tutien_tang', description='Tặng vật phẩm phổ thông cho bạn cùng server')
    @app_commands.guild_only()
    @app_commands.choices(item=[app_commands.Choice(name=R.NAMES[k], value=k) for k in sorted(R.TRADABLE)])
    async def gift(self, interaction: discord.Interaction, member: discord.Member, item: str,
                   count: app_commands.Range[int, 1, 100] = 1,
                   realm: app_commands.Range[int, 0, 4] = None, quality: str = 'normal'):
        args = {'item': item, 'count': count, 'target': member.id, 'quality': quality}
        if realm is not None:
            args['realm'] = realm
        await self.action(interaction, 'gift', args, True)

    @app_commands.command(name='tutien_bophieu', description='Bỏ phiếu công trình tông môn nên nâng cấp')
    @app_commands.guild_only()
    @app_commands.choices(building=[app_commands.Choice(name=v, value=k) for k, v in R.BUILDINGS.items()])
    async def vote(self, interaction: discord.Interaction, building: str):
        await self.action(interaction, 'vote', {'building': building}, False)

    @app_commands.command(name='tutien_nangcap', description='Chủ server thực hiện nâng cấp theo phiếu bầu')
    @app_commands.guild_only()
    async def upgrade(self, interaction: discord.Interaction, building: str):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message('Chỉ chủ server được nâng cấp công trình.', ephemeral=True)
            return
        await self.action(interaction, 'upgrade', {'building': building}, True)

    @app_commands.command(name='tutien_tui', description='Tìm kiếm và lọc túi vật phẩm')
    @app_commands.guild_only()
    async def bag_command(self, interaction: discord.Interaction, query: str = '',
                          realm: app_commands.Range[int, 0, 4] = None):
        await self.action(interaction, 'bag', {'query': query, 'realm': realm}, False)

    @app_commands.command(name='tutien_cauhinh', description='Bật/tắt game, bỏ qua kênh hoặc gộp bảng game')
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.choices(mode=[app_commands.Choice(name=n, value=v) for n, v in [
        ('Xem cấu hình','status'),('Bật game','enable'),('Tạm ngừng game','pause'),
        ('Bỏ qua XP kênh','ignore'),('Tính XP kênh trở lại','include'),
        ('Gộp bảng vào kênh tu tiên','merged'),('Tách ba kênh','separate')]])
    async def configure(self, interaction: discord.Interaction, mode: str = 'status',
                        channel: Optional[Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel]] = None):
        await interaction.response.defer(ephemeral=True)
        _, resources = await self.store.snapshot(interaction.guild_id)
        values = {}
        if mode in ('enable', 'pause'):
            values['enabled'] = mode == 'enable'
        elif mode in ('ignore', 'include'):
            if not channel or channel.guild.id != interaction.guild_id:
                await interaction.followup.send('Chọn kênh thuộc server này.', ephemeral=True)
                return
            ignored = set(resources.get('ignored_channels', []))
            ignored.add(channel.id) if mode == 'ignore' else ignored.discard(channel.id)
            values['ignored_channels'] = sorted(ignored)
        elif mode in ('merged', 'separate'):
            values['channel_mode'] = mode
        await self.store.configure(interaction.guild_id, values)
        self.ignored[interaction.guild_id] = values.get('ignored_channels', resources.get('ignored_channels', []))
        if mode in ('merged', 'separate'):
            await provision(self.bot, interaction.guild, self.store, Panel(self))
        _, resources = await self.store.snapshot(interaction.guild_id)
        await interaction.followup.send(f"Game: {resources.get('enabled', True)} · Kênh: {resources.get('channel_mode', 'separate')} · Bỏ qua XP: {resources.get('ignored_channels', [])}", ephemeral=True)

    @app_commands.command(name='tutien_doisoat', description='Quản trị viên xác nhận tài nguyên của lần thiết lập bị gián đoạn')
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reconcile(self, interaction: discord.Interaction, resource_id: str):
        await interaction.response.defer(ephemeral=True)
        try:
            async with self.store.provisioning_lock(interaction.guild_id):
                _, resources = await self.store.snapshot(interaction.guild_id)
                pending = resources.get('pending')
                E.require(pending is not None, 'Không có tài nguyên cần đối soát.')
                E.require(resource_id.isdigit(), 'Nhập ID tài nguyên Discord đã được tạo.')
                rid = int(resource_id)
                if pending.startswith('realm_role_'):
                    role = interaction.guild.get_role(rid)
                    index = int(pending.rsplit('_', 1)[1])
                    E.require(role and role.name == f'Tu Tiên · {R.REALMS[index]}' and not role.managed and
                              role.permissions.value == 0 and role < interaction.guild.me.top_role,
                              'Role không khớp cảnh giới/quyền/vị trí mong đợi.')
                else:
                    channel = interaction.guild.get_channel(rid)
                    if pending == 'category_id':
                        E.require(isinstance(channel, discord.CategoryChannel) and channel.name == 'Virtus · Tu Tiên',
                                  'Danh mục không khớp.')
                    else:
                        marker = f'virtus:{self.bot.user.id}:{interaction.guild_id}:{pending}'
                        E.require(isinstance(channel, discord.TextChannel) and channel.topic == marker,
                                  'Kênh không có dấu nhận diện bot phù hợp.')
                await self.store.resource(interaction.guild_id, pending, rid)
                await self.store.resource(interaction.guild_id, 'pending', None)
            await provision(self.bot, interaction.guild, self.store, Panel(self))
            await interaction.followup.send('Đã đối soát và tiếp tục thiết lập.', ephemeral=True)
        except (E.GameError, SetupError, discord.HTTPException) as error:
            await interaction.followup.send(str(error), ephemeral=True)

    @app_commands.command(name='tutien_setup', description='Kiểm tra hoặc chạy lại thiết lập tự động, không tạo trùng')
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            resources = await provision(self.bot, interaction.guild, self.store, Panel(self))
            await interaction.followup.send(f"Thiết lập: {resources.get('status', 'chưa bật')}. Dùng /tutien để bắt đầu.", ephemeral=True)
        except (SetupError, discord.HTTPException) as error:
            await interaction.followup.send(f'Thiết lập cần xử lý: {error}', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Cultivation(bot))
