"""One shared debt ledger per channel; no events or bill-closing workflow."""
import logging
import math
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from repositories.config import ConfigRepository
from repositories.feature_toggle import FeatureToggleRepository
from repositories.group_debt import GroupDebtRepository
from services.group_debt import MAX_MEMBERS, money, parse_amount, settlements, split_shares

log = logging.getLogger(__name__)
NO_MENTIONS = discord.AllowedMentions.none()


def mention(user_id):
    return f"<@{user_id}>"


class DebtView(discord.ui.View):
    def __init__(self, cog, owner_id=None, timeout=300):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.owner_id = owner_id

    async def interaction_check(self, interaction):
        if self.owner_id is not None and interaction.user.id != self.owner_id:
            await interaction.response.send_message("Dùng lệnh của bạn để thao tác nhé.", ephemeral=True)
            return False
        return await self.cog.interaction_check(interaction)

    async def on_error(self, interaction, error, item):
        await self.cog.send_error(interaction, error)


class GroupPicker(DebtView):
    def __init__(self, cog, interaction, group):
        super().__init__(cog, interaction.user.id)
        self.selected = list(group.member_ids) if group else [interaction.user.id]
        select = discord.ui.UserSelect(placeholder="Chọn lại toàn bộ thành viên của nhóm",
                                       min_values=1, max_values=MAX_MEMBERS, row=0)
        select.callback = self.choose
        self.picker = select
        self.add_item(select)

    def embed(self):
        return discord.Embed(title="Nhóm chia tiền của kênh", color=discord.Color.blue(),
            description="Thành viên: " + ', '.join(map(mention, self.selected)) +
            "\n\nChọn lại danh sách để thay đổi, rồi bấm **Lưu nhóm**."
            "\nĐổi thành viên không xóa nợ hoặc đổi các khoản đã ghi.")

    async def choose(self, interaction):
        members = self.picker.values
        if any(user.bot or not isinstance(user, discord.Member) or user.guild.id != interaction.guild_id for user in members):
            raise ValueError("Chỉ chọn người thật trong server này.")
        self.selected = sorted(user.id for user in members)
        await interaction.response.edit_message(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)

    @discord.ui.button(label="Lưu nhóm", style=discord.ButtonStyle.success, row=1)
    async def save(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.repo.configure(interaction.guild_id, interaction.channel_id,
            interaction.user.id, self.selected, manager=await self.cog.is_manager(interaction))
        await interaction.edit_original_response(content="Đã lưu nhóm. Dùng `/chia 600k` sau buổi chơi, `/no` để xem nợ.",
                                                  embed=self.embed(), view=None, allowed_mentions=NO_MENTIONS)
        self.stop()


class SplitPicker(DebtView):
    def __init__(self, cog, interaction, group, amount, note):
        super().__init__(cog, interaction.user.id)
        self.transaction_id = interaction.id
        self.revision = group.revision
        self.amount = amount
        self.note = note
        self.selected = list(group.member_ids)
        options = []
        for user_id in self.selected:
            member = interaction.guild.get_member(user_id)
            options.append(discord.SelectOption(label=(member.display_name if member else str(user_id))[:100],
                                                value=str(user_id), default=True))
        self.picker = discord.ui.Select(placeholder="Những người chơi hôm nay", options=options,
                                        min_values=1, max_values=len(options), row=0)
        self.picker.callback = self.choose
        self.add_item(self.picker)

    def embed(self):
        shares = split_shares(self.amount, self.selected)
        text = f"Bạn ứng **{money(self.amount)}**. Chia cho **{len(shares)} người**:\n"
        text += '\n'.join(f"{mention(uid)}: {money(value)}" for uid, value in shares.items())
        if self.note:
            text += "\nGhi chú: " + discord.utils.escape_markdown(self.note)
        text += "\n\nBỏ chọn người không chơi. Nợ chỉ được ghi khi bấm **Xác nhận chia tiền**."
        return discord.Embed(title="Chia tiền buổi chơi", description=text, color=discord.Color.blue())

    async def choose(self, interaction):
        self.selected = [int(value) for value in self.picker.values]
        for option in self.picker.options:
            option.default = int(option.value) in self.selected
        await interaction.response.edit_message(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)

    @discord.ui.button(label="Xác nhận chia tiền", style=discord.ButtonStyle.success, row=1)
    async def confirm(self, interaction, button):
        # Defer a message update so edit_original_response removes the original picker.
        await interaction.response.defer()
        transaction, created = await self.cog.repo.record(
            self.transaction_id, interaction.guild_id, interaction.channel_id, interaction.user.id,
            'expense', self.amount, participants=list(self.selected), revision=self.revision, note=self.note)
        await interaction.edit_original_response(content="Đã ghi vào sổ nợ. Dùng `/no` để xem số dư.",
                                                  embed=None, view=None)
        self.stop()
        if created:
            await self.cog.send_receipt(interaction, transaction)

    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.secondary, row=1)
    async def cancel(self, interaction, button):
        await interaction.response.edit_message(content="Đã hủy, chưa ghi nợ.", embed=None, view=None)
        self.stop()


class UndoView(DebtView):
    """A single persistent handler; the receipt footer identifies the DB transaction."""
    def __init__(self, cog):
        super().__init__(cog, timeout=None)

    @discord.ui.button(label="Hoàn tác", style=discord.ButtonStyle.secondary, custom_id="group_debt:undo")
    async def undo(self, interaction, button):
        message = interaction.message
        if not message or not message.embeds or not message.embeds[0].footer.text:
            raise ValueError("Dùng /hoantac với mã giao dịch trong /lichsu.")
        transaction_id = int(message.embeds[0].footer.text.removeprefix("Giao dịch #"))
        await interaction.response.defer(ephemeral=True, thinking=True)
        changed = await self.cog.repo.undo(transaction_id, interaction.guild_id, interaction.channel_id,
                                          interaction.user.id, manager=await self.cog.is_manager(interaction))
        embed = message.embeds[0].copy()
        embed.title = "Đã hoàn tác"
        embed.color = discord.Color.greyple()
        await message.edit(embed=embed, view=None, allowed_mentions=NO_MENTIONS)
        await interaction.followup.send("Đã hoàn tác và cập nhật số dư." if changed else "Khoản này đã được hoàn tác trước đó.",
                                        ephemeral=True)


class GroupDebtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = GroupDebtRepository()
        self.config_repo = ConfigRepository()
        self.feature_repo = FeatureToggleRepository()
        self.undo_view = UndoView(self)

    async def cog_load(self):
        self.bot.add_view(self.undo_view)

    async def cog_unload(self):
        for view in self.bot.persistent_views:
            if isinstance(view, UndoView) and view.cog is self:
                view.stop()

    async def interaction_check(self, interaction):
        if not interaction.guild_id or not interaction.channel_id:
            await interaction.response.send_message("Dùng chức năng này trong kênh của server nhé.", ephemeral=True)
            return False
        if not await self.feature_repo.get(interaction.guild_id, 'group_debt'):
            await interaction.response.send_message("Chia tiền nhóm chưa bật. Bật Group Debt trong Admin Dashboard.", ephemeral=True)
            return False
        config = await self.config_repo.get(interaction.guild_id, 'CHANNEL_GROUP_DEBT_IDS', '')
        allowed = {int(value.strip()) for value in config.split(',') if value.strip().isdigit()}
        if allowed and interaction.channel_id not in allowed:
            await interaction.response.send_message("Kênh này chưa được cho phép chia tiền nhóm.", ephemeral=True)
            return False
        return True

    async def is_manager(self, interaction):
        if interaction.user.guild_permissions.manage_guild:
            return True
        config = await self.config_repo.get(interaction.guild_id, 'ADMIN_IDS', '')
        return str(interaction.user.id) in {value.strip() for value in config.split(',')}

    async def send_error(self, interaction, error):
        original = getattr(error, 'original', error)
        if isinstance(original, ValueError):
            text = str(original)
        else:
            log.error("Group debt operation failed", exc_info=(type(original), original, original.__traceback__))
            text = "Có lỗi khi xử lý. Kiểm tra /lichsu trước khi nhập lại; khoản đã ghi sẽ hiện ở đó."
        if interaction.response.is_done():
            await interaction.followup.send(text, ephemeral=True)
        else:
            await interaction.response.send_message(text, ephemeral=True)

    async def cog_app_command_error(self, interaction, error):
        await self.send_error(interaction, error)

    async def send_receipt(self, interaction, transaction):
        if transaction.kind == 'expense':
            text = f"{mention(transaction.actor_id)} ứng **{money(transaction.amount)}**.\n"
            text += '\n'.join(f"{mention(int(uid))}: {money(value)}" for uid, value in transaction.shares.items())
            title = "Đã chia tiền"
        else:
            text = f"{mention(transaction.actor_id)} đã trả {mention(transaction.recipient_id)} **{money(transaction.amount)}**."
            title = "Đã ghi trả tiền"
        if transaction.note:
            text += '\nGhi chú: ' + discord.utils.escape_markdown(transaction.note)
        text += "\nDùng `/no` để xem nợ hiện tại."
        embed = discord.Embed(title=title, description=text, color=discord.Color.green())
        embed.set_footer(text=f"Giao dịch #{transaction.id}")
        await interaction.followup.send(embed=embed, view=UndoView(self), ephemeral=False, allowed_mentions=NO_MENTIONS)

    @app_commands.command(name="nhom", description="Chọn thành viên thường chơi trong kênh này (thiết lập một lần)")
    @app_commands.guild_only()
    async def group(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        group = await self.repo.get_group(interaction.guild_id, interaction.channel_id)
        if group and group.owner_id != interaction.user.id and not await self.is_manager(interaction):
            raise ValueError("Chỉ người tạo nhóm hoặc quản trị viên được thay đổi nhóm.")
        view = GroupPicker(self, interaction, group)
        await interaction.followup.send(embed=view.embed(), view=view, ephemeral=True, allowed_mentions=NO_MENTIONS)

    @app_commands.command(name="chia", description="Bạn vừa ứng tiền: chọn người chơi rồi xác nhận để chia đều")
    @app_commands.describe(tien="Tiền bạn đã trả, ví dụ 600000 hoặc 600k", ghichu="Ghi chú tùy chọn")
    @app_commands.guild_only()
    async def split(self, interaction: discord.Interaction, tien: str, ghichu: Optional[str] = None):
        amount = parse_amount(tien)
        note = (ghichu or '').strip()
        if len(note) > 100:
            raise ValueError("Ghi chú tối đa 100 ký tự.")
        await interaction.response.defer(ephemeral=True)
        group = await self.repo.get_group(interaction.guild_id, interaction.channel_id)
        if not group:
            raise ValueError("Dùng /nhom để chọn thành viên trước.")
        if interaction.user.id not in group.member_ids:
            raise ValueError("Bạn chưa thuộc nhóm. Nhờ người tạo nhóm cập nhật /nhom.")
        view = SplitPicker(self, interaction, group, amount, note)
        await interaction.followup.send(embed=view.embed(), view=view, ephemeral=True, allowed_mentions=NO_MENTIONS)

    @app_commands.command(name="no", description="Xem số nợ cộng dồn và gợi ý ai chuyển tiền cho ai")
    @app_commands.guild_only()
    async def balance(self, interaction: discord.Interaction, trang: app_commands.Range[int, 1] = 1):
        await interaction.response.defer()
        balances = await self.repo.summary(interaction.guild_id, interaction.channel_id)
        transfers = settlements(balances)
        rows = sorted(balances.items())
        pages = max(1, math.ceil(max(len(rows), len(transfers)) / 20))
        if trang > pages:
            raise ValueError(f"Chỉ có {pages} trang.")
        offset = (trang - 1) * 20
        lines = []
        for uid, value in rows[offset:offset + 20]:
            status = f"được nhận **{money(value)}**" if value > 0 else f"cần trả **{money(-value)}**" if value < 0 else "hết nợ"
            lines.append(f"{mention(uid)}: {status}")
        embed = discord.Embed(title="Sổ nợ nhóm của kênh", description='\n'.join(lines), color=discord.Color.blue())
        suggestions = [f"{mention(sender)} → {mention(recipient)}: **{money(amount)}**"
                       for sender, recipient, amount in transfers[offset:offset + 20]]
        # Keep each field under Discord's 1024-character limit.
        for start in range(0, len(suggestions), 8):
            embed.add_field(name="Gợi ý chuyển tiền", value='\n'.join(suggestions[start:start + 8]), inline=False)
        if not transfers:
            embed.add_field(name="Đã cân bằng", value="Mọi người đều hết nợ.", inline=False)
        embed.set_footer(text=f"Trang {trang}/{pages} · /tra để ghi đã trả · Đây là nợ ròng trong nhóm")
        await interaction.followup.send(embed=embed, allowed_mentions=NO_MENTIONS)

    @app_commands.command(name="tra", description="Ghi bạn đã trả tiền cho một người, tự trừ nợ (không cần duyệt)")
    @app_commands.describe(nguoi="Người đã nhận tiền", tien="Tiền đã trả, ví dụ 200000 hoặc 200k")
    @app_commands.guild_only()
    async def pay(self, interaction: discord.Interaction, nguoi: discord.Member, tien: str):
        amount = parse_amount(tien)
        if nguoi.bot:
            raise ValueError("Không thể trả tiền cho bot.")
        await interaction.response.defer()
        transaction, created = await self.repo.record(interaction.id, interaction.guild_id, interaction.channel_id,
            interaction.user.id, 'payment', amount, recipient_id=nguoi.id)
        if created:
            await self.send_receipt(interaction, transaction)
        else:
            await interaction.followup.send("Khoản này đã được ghi trước đó.", ephemeral=True)

    @app_commands.command(name="lichsu", description="Xem các khoản chia tiền, trả tiền và mã để hoàn tác")
    @app_commands.guild_only()
    async def history(self, interaction: discord.Interaction, trang: app_commands.Range[int, 1] = 1):
        await interaction.response.defer(ephemeral=True)
        rows = await self.repo.history(interaction.guild_id, interaction.channel_id, trang)
        lines = []
        for row in rows:
            text = f"{mention(row.actor_id)} " + ("ứng" if row.kind == 'expense' else f"trả {mention(row.recipient_id)}")
            text += f" **{money(row.amount)}**"
            if row.note:
                text += " — " + discord.utils.escape_markdown(row.note)
            if row.reversed:
                text += " · **Đã hoàn tác**"
            lines.append(f"`{row.id}` · <t:{int(row.created_at.timestamp())}:d>\n{text}")
        embed = discord.Embed(title=f"Lịch sử · Trang {trang}", description='\n\n'.join(lines) or "Chưa có giao dịch ở trang này.")
        embed.set_footer(text="/lichsu trang:2 để xem tiếp · /hoantac ma:<mã giao dịch>")
        await interaction.followup.send(embed=embed, ephemeral=True, allowed_mentions=NO_MENTIONS)

    @app_commands.command(name="hoantac", description="Hủy một khoản bạn nhập nhầm; giữ lại dấu vết trong lịch sử")
    @app_commands.describe(ma="Mã giao dịch trong /lichsu")
    @app_commands.guild_only()
    async def undo(self, interaction: discord.Interaction, ma: str):
        if not ma.isascii() or not ma.isdigit() or len(ma) > 19 or int(ma) > 2**63 - 1:
            raise ValueError("Mã giao dịch không hợp lệ. Xem /lichsu để lấy mã.")
        await interaction.response.defer(ephemeral=True)
        changed = await self.repo.undo(int(ma), interaction.guild_id, interaction.channel_id,
                                      interaction.user.id, manager=await self.is_manager(interaction))
        await interaction.followup.send("Đã hoàn tác và cập nhật số dư." if changed else "Khoản này đã được hoàn tác trước đó.",
                                        ephemeral=True)


async def setup(bot):
    await bot.add_cog(GroupDebtCog(bot))
