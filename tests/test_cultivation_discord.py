import copy
import unittest
from contextlib import asynccontextmanager
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, MagicMock

import discord
from services.cultivation.bootstrap import provision, SetupError
from bot.cogs.cultivation import eligible_voice


class MemoryStore:
    def __init__(self):
        self.resources = {}

    @asynccontextmanager
    async def provisioning_lock(self, gid):
        yield

    async def snapshot(self, gid):
        return {}, copy.deepcopy(self.resources)

    async def resource(self, gid, key, value):
        self.resources[key] = value


class DiscordTests(unittest.IsolatedAsyncioTestCase):
    async def test_repeated_setup_preserves_existing_resources(self):
        store = MemoryStore()
        guild = MagicMock()
        guild.id = 123
        guild.me.guild_permissions.manage_channels = True
        guild.me.guild_permissions.manage_roles = True
        bot = NS(user=NS(id=99))
        channels, roles = {}, {}
        ids = iter(range(1000, 1100))
        guild.get_channel.side_effect = channels.get
        guild.get_role.side_effect = roles.get
        async def category(*args, **kwargs):
            value = MagicMock(spec=discord.CategoryChannel)
            value.id = next(ids)
            channels[value.id] = value
            return value
        async def channel(*args, **kwargs):
            value = MagicMock(spec=discord.TextChannel)
            value.id = next(ids)
            async def history(**kwargs):
                for v in []:
                    yield v
            value.history = history
            message = NS(id=999)
            value.send = AsyncMock(return_value=message)
            value.fetch_message = AsyncMock(return_value=message)
            channels[value.id] = value
            return value
        async def role(*args, **kwargs):
            value = MagicMock(spec=discord.Role)
            value.id = next(ids)
            value.__ge__.return_value = False
            roles[value.id] = value
            return value
        guild.create_category = AsyncMock(side_effect=category)
        guild.create_text_channel = AsyncMock(side_effect=channel)
        guild.create_role = AsyncMock(side_effect=role)
        # Same-name unrelated resources must never be adopted or overwritten.
        unrelated = NS(id=33, name='tu-tien')
        channels[33] = unrelated
        await provision(bot, guild, store, None)
        await provision(bot, guild, store, None)
        self.assertEqual(guild.create_category.await_count, 1)
        self.assertEqual(guild.create_text_channel.await_count, 3)
        self.assertEqual(guild.create_role.await_count, 5)
        self.assertIs(channels[33], unrelated)
        self.assertEqual(store.resources['status'], 'ready')

    async def test_uncertain_creation_stops_without_duplicate(self):
        store = MemoryStore()
        store.resources['pending'] = 'category_id'
        guild = MagicMock()
        guild.id = 123
        guild.get_channel.return_value = None
        guild.create_category = AsyncMock()
        with self.assertRaises(SetupError):
            await provision(NS(user=NS(id=99)), guild, store, None)
        guild.create_category.assert_not_called()

    def test_voice_eligibility(self):
        def member(uid, bot=False, deaf=False, mute=False):
            return NS(id=uid, bot=bot, voice=NS(self_deaf=deaf, deaf=False, afk=False, suppress=False, self_mute=mute))
        a, b = member(1), member(2, mute=True)
        channel = NS(members=[a, b, member(3, bot=True), member(4, deaf=True)])
        guild = NS(voice_channels=[channel], stage_channels=[], afk_channel=None)
        self.assertEqual(set(eligible_voice(guild)), {1, 2})
        channel.members = [a, member(3, bot=True)]
        self.assertFalse(eligible_voice(guild))
        channel.members = [a, b]
        guild.afk_channel = channel
        self.assertFalse(eligible_voice(guild))
