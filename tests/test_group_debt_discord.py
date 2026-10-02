from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock

import discord
from bot.cogs.group_debt import GroupDebtCog, GroupPicker, SplitPicker, UndoView


def interaction(user_id=1):
    user = SimpleNamespace(id=user_id, guild_permissions=SimpleNamespace(manage_guild=False))
    return SimpleNamespace(
        id=123456789, guild_id=10, channel_id=20, user=user,
        guild=SimpleNamespace(get_member=lambda uid: SimpleNamespace(display_name=f'Player {uid}')),
        response=SimpleNamespace(defer=AsyncMock(), send_message=AsyncMock(), edit_message=AsyncMock(),
                                 is_done=MagicMock(return_value=False)),
        followup=SimpleNamespace(send=AsyncMock()), edit_original_response=AsyncMock(),
    )


class DiscordDebtFlow(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.cog = GroupDebtCog(SimpleNamespace(add_view=MagicMock(), persistent_views=[]))
        self.cog.repo = AsyncMock()
        self.cog.feature_repo = SimpleNamespace(get=AsyncMock(return_value=True))
        self.cog.config_repo = SimpleNamespace(get=AsyncMock(return_value=''))
        self.group = SimpleNamespace(member_ids=[1, 2, 3], revision=1, owner_id=1)

    async def test_split_defaults_to_everyone_and_no_write_until_confirm(self):
        request = interaction()
        self.cog.repo.get_group.return_value = self.group
        await self.cog.split.callback(self.cog, request, '600k')
        view = request.followup.send.call_args.kwargs['view']
        self.assertEqual(view.selected, [1, 2, 3])
        self.assertTrue(all(option.default for option in view.picker.options))
        self.assertIn('200.000 ₫', view.embed().description)
        self.cog.repo.record.assert_not_awaited()
        # A user removes the player who did not come today.
        view.picker._values = ['1', '2']
        selection = interaction()
        await view.choose(selection)
        self.assertEqual(view.selected, [1, 2])
        self.assertIn('300.000 ₫', view.embed().description)
        self.cog.repo.record.assert_not_awaited()
        row = SimpleNamespace(id=request.id, actor_id=1, kind='expense', amount=600000,
                              shares={'1': 300000, '2': 300000}, note='')
        self.cog.repo.record.return_value = (row, True)
        confirm = interaction()
        confirm.id = 999  # Record using the ORIGINAL request, not the button's ID.
        await view.confirm.callback(confirm)
        confirm.response.defer.assert_awaited_once_with()
        self.cog.repo.record.assert_awaited_once_with(request.id, 10, 20, 1, 'expense', 600000,
                                                     participants=[1, 2], revision=1, note='')
        receipt = confirm.followup.send.call_args.kwargs
        self.assertFalse(receipt['ephemeral'])
        self.assertIsInstance(receipt['view'], UndoView)
        self.assertEqual(receipt['embed'].footer.text, f'Giao dịch #{request.id}')
        view.stop()

    async def test_cancel_does_not_record_debt(self):
        view = SplitPicker(self.cog, interaction(), self.group, 600000, '')
        await view.cancel.callback(interaction())
        self.cog.repo.record.assert_not_awaited()
        self.assertTrue(view.is_finished())

    async def test_someone_else_cannot_operate_your_preview(self):
        view = SplitPicker(self.cog, interaction(), self.group, 600000, '')
        other = interaction(2)
        self.assertFalse(await view.interaction_check(other))
        other.response.send_message.assert_awaited_once()
        self.cog.repo.record.assert_not_awaited()
        view.stop()

    async def test_disabled_feature_and_channel_restrictions_apply_to_buttons(self):
        view = SplitPicker(self.cog, interaction(), self.group, 600000, '')
        self.cog.feature_repo.get.return_value = False
        self.assertFalse(await view.interaction_check(interaction()))
        self.cog.feature_repo.get.return_value = True
        self.cog.config_repo.get.return_value = '21, 22'
        self.assertFalse(await view.interaction_check(interaction()))
        self.cog.config_repo.get.return_value = '20'
        self.assertTrue(await view.interaction_check(interaction()))
        view.stop()

    async def test_duplicate_confirmation_does_not_post_second_receipt(self):
        view = SplitPicker(self.cog, interaction(), self.group, 600000, '')
        self.cog.repo.record.return_value = (SimpleNamespace(), False)
        confirm = interaction()
        await view.confirm.callback(confirm)
        confirm.followup.send.assert_not_awaited()
        self.assertTrue(view.is_finished())

    async def test_persistent_undo_reads_receipt_after_restart(self):
        # Construct a fresh view with no transaction in memory.
        view = UndoView(self.cog)
        self.assertTrue(view.is_persistent())
        click = interaction()
        embed = discord.Embed(title='Đã chia tiền')
        embed.set_footer(text='Giao dịch #98765')
        click.message = SimpleNamespace(embeds=[embed], edit=AsyncMock())
        self.cog.repo.undo.return_value = True
        await view.undo.callback(click)
        self.cog.repo.undo.assert_awaited_once_with(98765, 10, 20, 1, manager=False)
        self.assertIsNone(click.message.edit.call_args.kwargs['view'])
        view.stop()

    async def test_group_setup_saves_and_old_selection_is_kept(self):
        request = interaction()
        view = GroupPicker(self.cog, request, self.group)
        self.assertEqual(view.selected, [1, 2, 3])
        await view.save.callback(request)
        self.cog.repo.configure.assert_awaited_once_with(10, 20, 1, [1, 2, 3], manager=False)
        self.assertTrue(view.is_finished())

    async def test_no_splits_large_ledger_into_discord_sized_fields(self):
        self.cog.repo.summary.return_value = {**{uid: -100000 for uid in range(1, 26)}, 30: 2500000}
        request = interaction()
        await self.cog.balance.callback(self.cog, request)
        embed = request.followup.send.call_args.kwargs['embed']
        self.assertLessEqual(len(embed.description), 4096)
        self.assertTrue(all(len(field.value) <= 1024 for field in embed.fields))
        self.assertLessEqual(len(embed), 6000)
        self.assertIn('1/2', embed.footer.text)

    async def test_reconfigured_group_blocks_stale_preview(self):
        view = SplitPicker(self.cog, interaction(), self.group, 600000, '')
        self.cog.repo.record.side_effect = ValueError('Nhóm vừa thay đổi')
        with self.assertRaisesRegex(ValueError, 'thay đổi'):
            await view.confirm.callback(interaction())
        view.stop()
