__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import io
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.Prefix import Prefix
from Configs.Config import Config
from Utils.TestIdGenerator import TestIdGenerator
from Utils.test_utils import get_cogs_messages
from Bot.Core.ScrimClient import ScrimClient
from Utils.AsyncUnittestBase import AsyncUnittestBase


class TestScrimClient(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.config = MagicMock()
        self.config.file_folder = Config().file_folder
        self.config.token = Config().token
        self.context_provider = AsyncMock()
        self.client = ScrimClient(self.config, self.context_provider, self.loop)

    @patch('sys.stdout', new_callable=io.StringIO)
    async def test_setup_cogs_when_called_then_cogs_loaded(self, print_catcher):
        self.client.setup_cogs()
        output = print_catcher.getvalue()
        self.assertTrue(len(output))
        for cog_message in get_cogs_messages():
            self.assertIn(cog_message, output.splitlines())

    @unittest.skipUnless(os.getenv("LONG_TESTS") == "True", "Skipped long test")
    @patch('sys.stdout', new_callable=io.StringIO)
    async def test_start_bot_when_called_then_bot_started_and_connected(self, print_catcher):
        asyncio.create_task(self.client.start_bot())
        await self.client.connected.wait()
        output = print_catcher.getvalue()
        self.assertEqual(f"Attempting a connection to Discord...\n"
                         f"Successfully logged in as ScrimBot2.0, with version {__version__}\n", output)
        await self.client.close()

    async def test_get_prefix_when_no_guild_specific_prefix_then_default_prefix_returned(self):
        mock_message = self._mock_prefixes([])
        self.assertEqual(self.config.default_prefix, await self.client.get_prefix(mock_message))

    async def test_get_prefix_when_guild_has_one_prefix_then_guild_prefix_returned(self):
        prefixes = [f"{Config.default_prefix}:"]
        mock_message = self._mock_prefixes(prefixes)
        self.assertEqual(prefixes, await self.client.get_prefix(mock_message))

    async def test_get_prefix_when_guild_has_multiple_prefixes_then_all_guild_prefix_returned(self):
        prefixes = ["1", "2", "3"]
        mock_message = self._mock_prefixes(prefixes)
        self.assertEqual(prefixes, await self.client.get_prefix(mock_message))

    async def test_get_deletion_time_when_no_guild_specific_time_then_default_time_returned(self):
        mock_guild = self._mock_timeout(None)
        self.assertEqual(self.config.default_timeout, await self.client.get_deletion_time(mock_guild))

    async def test_get_deletion_time_when_guild_specific_time_exists_then_guild_deletion_time_returned(self):
        mock_guild = self._mock_timeout(self.config.default_timeout + 1)
        self.assertEqual(self.config.default_timeout + 1, await self.client.get_deletion_time(mock_guild))

    async def test_get_context_given_provider_exists_then_called_with_super_and_message(self):
        mock_message = MagicMock()
        await self.client.get_context(mock_message)
        await_args = self.context_provider.get_context.await_args
        # TODO fix this atrocity or learn to live with it
        self.assertEqual("<super: <class 'ScrimClient'>, <ScrimClient object>>", str(await_args[0][0]))
        self.assertEqual(mock_message, await_args[0][1])

    def _mock_timeout(self, timeout):
        mock_guild = MagicMock()
        mock_guild.id = self.id_mocker.generate_viable_id()
        mock_guild.scrim_timeout = timeout
        mock_converter = MagicMock()
        mock_converter.convert = MagicMock(return_value=mock_guild)
        Guild.set_converter(mock_converter)
        return mock_guild

    def _mock_prefixes(self, prefixes):
        mock_message = MagicMock()
        mock_message.guild.id = self.id_mocker.generate_viable_id()
        mock_converter = MagicMock()
        mock_guild = MagicMock()
        mock_guild.prefixes = prefixes
        mock_converter.convert = MagicMock(return_value=mock_guild)
        Guild.set_converter(mock_converter)
        return mock_message
