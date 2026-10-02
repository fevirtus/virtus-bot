"""Ensure the remaining bot can load without the retired game or its schema."""
import unittest
import models
from infra.db.base import Base
from bot.core.bot import VirtusBot


class LegacyModules(unittest.IsolatedAsyncioTestCase):
    async def test_remaining_extensions_load_and_register_commands(self):
        async with VirtusBot() as bot:
            for name in ('home_debt', 'group_debt', 'score', 'noi_tu', 'football'):
                await bot.load_extension('bot.cogs.'+name)
            self.assertEqual(len(bot.extensions), 5)
            self.assertTrue(bot.tree.get_commands())
            self.assertTrue({'nhom', 'chia', 'no', 'tra', 'lichsu', 'hoantac'}.issubset(
                {c.name for c in bot.tree.get_commands()}))
            self.assertTrue(any(view.is_persistent() for view in bot.persistent_views))
            self.assertFalse(any(c.name.startswith('tutien') for c in bot.tree.get_commands()))

    def test_startup_schema_excludes_retired_tables(self):
        self.assertTrue({'guilds', 'bot_configs', 'home_debt', 'score'}.issubset(Base.metadata.tables))
        self.assertFalse(any(name.startswith('cultivation_') for name in Base.metadata.tables))
        self.assertTrue({'group_debt_groups', 'group_debt_transactions', 'group_debt_entries'}.issubset(Base.metadata.tables))
