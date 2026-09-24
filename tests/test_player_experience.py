import copy
import random
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, MagicMock, patch

import discord
from bot.cogs.cultivation import Cultivation, Personal, activity_text, profile_text
from services.cultivation import engine as E, rules as R
from services.cultivation.combat import battle
from services.cultivation.presentation import aptitude_text, progress_lines


class PlayerExperience(unittest.TestCase):
    def setUp(self):
        self.now = 1800000000
        self.state = E.initial()
        self.p = E.player(self.state, 1, 'One', self.now, random.Random(1))

    def test_roll_comparison_has_meaning_no_internal_dicts_or_old_fight(self):
        E.execute(self.state, 1, 'roll', {}, self.now, random.Random(3), 'roll')
        self.p['inbox'].append({'time': self.now, 'text': 'OLD_FIGHT'})
        text = aptitude_text(self.p)
        for term in ('Tư chất là gì', 'CHƯA áp dụng', 'Sinh lực', 'Công kích', 'So với hiện tại', 'Kiếp số', 'Thiên phú'):
            self.assertIn(term, text)
        for term in ("{'", "'stats'", 'balanced', 'OLD_FIGHT'):
            self.assertNotIn(term, text+profile_text(self.state, 1))
        self.assertLess(len(text), 3900)

    def test_explore_after_restart_reports_exact_rewards_once_without_dm(self):
        self.p['xp'] = R.cap(self.p)
        E.execute(self.state, 1, 'explore', {'area': 'herb'}, self.now, random.Random(2), 'trip')
        job = self.state['jobs']['trip']
        amount = job['results']['1']['items']['0:herb:normal']
        text = '\n'.join(progress_lines(self.state, 1, self.now+100))
        self.assertIn('tìm Linh thảo', text)
        self.assertNotIn(str(amount)+' Linh thảo', text)  # No premature result disclosure.
        resumed = copy.deepcopy(self.state)
        E.settle(resumed, self.now+1201)
        E.settle(resumed, self.now+1202)
        p = resumed['players']['1']
        self.assertEqual(E.bag(p, 'herb'), amount)
        self.assertEqual(p['coins'], 175)
        self.assertEqual(len(p['inbox']), 1)
        self.assertFalse(resumed['outbox'])  # DM remains opt-in.
        result = activity_text(resumed, 1)
        self.assertIn(f'Linh thảo ×{amount}', result)
        self.assertIn('Tu vi thực nhận: **+0**', result)
        self.assertIn('đầy thanh tu vi', result)
        self.assertIn('Đã hoàn tất', result)

    def test_craft_shows_quantity_quality_and_completion(self):
        E.give(self.p, 'herb', 4)
        E.give(self.p, 'water', 2)
        E.execute(self.state, 1, 'craft', {'item': 'minor', 'count': 2}, self.now, random.Random(2), 'craft')
        self.assertIn('Tụ Khí Đan', '\n'.join(progress_lines(self.state, 1, self.now)))
        E.settle(self.state, self.now+121)
        self.assertIn('Tụ Khí Đan ×2', self.p['inbox'][-1]['text'])
        self.assertTrue(self.p['activity_tracking'])

    def test_party_results_and_encounter_changes_use_settled_amount(self):
        E.player(self.state, 2, 'Two', self.now, random.Random(2))
        stage = {'won': True, 'seconds': 30, 'log': [], 'participants': {
            u: {'used': 0, 'health': .8, 'mana': 50, 'damage': 200} for u in ('1', '2')}}
        with patch('services.cultivation.engine.battle', return_value=copy.deepcopy(stage)):
            E.start_battle(self.state, ['1', '2'], 'dungeon', self.now, random.Random(2), 'team')
        E.execute(self.state, 1, 'dungeon_event', {'choice': 'open'}, self.now+31, random.Random(1), 'choice')
        coins = self.state['jobs']['team']['results']['1']['coins']
        E.settle(self.state, self.now+200)
        for uid in ('1', '2'):
            p = self.state['players'][uid]
            self.assertTrue(p['activity_tracking'])
            self.assertIn(f'Linh thạch: **+{coins}**', p['inbox'][-1]['text'])
            self.assertIn('Phó bản', p['inbox'][-1]['text'])

    def test_old_pending_jobs_upgrade_without_losing_rewards(self):
        self.state['jobs']['old'] = {'kind': 'explore', 'realm': 0, 'users': ['1'], 'due': self.now,
                                    'results': {'1': {'message': 'Thám hiểm hoàn tất', 'items': {'0:water:normal': 4}, 'coins': 25, 'xp': 20}}}
        E.settle(self.state, self.now+1)
        self.assertTrue(self.p['activity_tracking'])
        self.assertIn('Linh tuyền ×4', activity_text(self.state, 1))

    def test_defiant_talent_does_not_replace_skill_multiplier(self):
        base = copy.deepcopy(self.p)
        base.update(_health=.29, _potions=0)
        base['genetics']['talents'] = []
        talented = copy.deepcopy(base)
        talented['genetics']['talents'] = ['Nghịch Thiên']
        # Both survive to a skill turn; compare identical RNG, low HP throughout.
        with patch('services.cultivation.combat.random.Random') as random_class:
            rng = random_class.return_value
            rng.randrange.return_value = 0
            rng.uniform.return_value = 1
            rng.random.return_value = 1
            rng.choice.side_effect = lambda a: a[0]
            normal = battle([('1', base)], 0, 'boss', 1)
            enhanced = battle([('1', talented)], 0, 'boss', 1)
        self.assertGreater(enhanced['participants']['1']['damage'], normal['participants']['1']['damage'])


class ActivityDelivery(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.state = E.initial()
        p = E.player(self.state, 1, 'One', 1800000000, random.Random(1))
        p['activity_tracking'] = True
        self.resources = {'game_channel': 20}
        self.message = NS(id=30, edit=AsyncMock())
        self.channel = NS(id=20, send=AsyncMock(return_value=self.message), fetch_message=AsyncMock(return_value=self.message))
        async def history(**kwargs):
            for m in []:
                yield m
        self.channel.history = history
        self.guild = NS(id=10, get_channel=lambda i: self.channel if i == 20 else None, get_member=lambda i: NS(id=i))
        self.cog = Cultivation(NS(user=NS(id=99)))
        self.cog.store = NS(snapshot=AsyncMock(side_effect=lambda gid: (copy.deepcopy(self.state), copy.deepcopy(self.resources))), resource=AsyncMock(side_effect=self.save))

    async def save(self, gid, key, value):
        self.resources[key] = value

    async def test_new_message_cached_then_edited_after_restart_without_duplicate(self):
        await self.cog.update_activities(self.guild)
        await self.cog.update_activities(self.guild)
        self.channel.send.assert_awaited_once()
        self.message.edit.assert_not_awaited()
        self.cog.activity_cache.clear()  # Simulate process restart, persistent DB pointer stays.
        await self.cog.update_activities(self.guild)
        self.channel.send.assert_awaited_once()
        self.message.edit.assert_awaited_once()
        self.assertIn('/10/20/30', await self.cog.activity_link(self.guild, 1))

    async def test_discord_failure_is_retried_without_dropping_result(self):
        error = discord.HTTPException(NS(status=503, reason='Unavailable'), 'try later')
        self.channel.send.side_effect = [error, self.message]
        E.inbox(self.state['players']['1'], 'Linh thảo ×4', 1800000000, activity=True)
        await self.cog.update_activities(self.guild)
        self.assertNotIn('activity_message_1', self.resources)
        await self.cog.update_activities(self.guild)
        self.assertIn('activity_message_1', self.resources)
        self.assertIn('Linh thảo ×4', self.channel.send.call_args.kwargs['embed'].description)

    async def test_help_actions_are_directly_available(self):
        view = Personal(self.cog, 1)
        labels = [getattr(c, 'label', '') for c in view.children]
        self.assertIn('Tư chất & thiên phú', labels)
        self.assertIn('Hướng dẫn', labels)
        self.assertIn('Hộp thư', labels)
        self.assertEqual(len(view.to_components()), 5)

    async def test_private_navigation_edits_panel_but_public_panel_is_preserved(self):
        from bot.cogs.cultivation import personal_reply
        interaction = NS(message=NS(flags=NS(ephemeral=True)), edit_original_response=AsyncMock(),
                         followup=NS(send=AsyncMock()))
        await personal_reply(interaction, 'Hướng dẫn')
        interaction.edit_original_response.assert_awaited_once()
        interaction.followup.send.assert_not_awaited()
        interaction.message.flags.ephemeral = False
        await personal_reply(interaction, 'Hướng dẫn')
        interaction.followup.send.assert_awaited_once()
        self.assertTrue(interaction.followup.send.call_args.kwargs['ephemeral'])

    async def test_reused_private_message_does_not_reuse_economic_receipt(self):
        from bot.cogs.cultivation import Confirm
        cog = NS(store=NS(act=AsyncMock(return_value='Đã mua')), sync_roles=AsyncMock())
        interaction = NS(message=NS(id=10), id=88, guild_id=1, guild=NS(owner_id=1),
                         user=NS(id=1, display_name='One'), response=NS(defer=AsyncMock(), send_message=AsyncMock()),
                         edit_original_response=AsyncMock())
        for origin in (100, 101):
            view = Confirm(cog, 1, 'buy', {'item': 'herb'}, 'quote', origin)
            await view.confirm.callback(interaction)
            await view.confirm.callback(interaction)  # Repeat click is locally rejected.
        keys = [call.args[3] for call in cog.store.act.call_args_list]
        self.assertEqual(keys, ['confirm:100', 'confirm:101'])
