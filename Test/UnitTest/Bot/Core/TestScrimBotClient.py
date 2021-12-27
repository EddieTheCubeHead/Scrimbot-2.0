__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import io
import os
import unittest
from logging import DEBUG
from unittest.mock import MagicMock, patch, AsyncMock, call

from Bot.Exceptions.BotBaseException import BotBaseException
from Bot.Exceptions.BotBaseInternalSystemException import BotBaseInternalSystemException
from Bot.Exceptions.BotUnrecognizedCommandException import BotUnrecognizedCommandException
from Configs.Config import Config
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Utils.TestHelpers.test_utils import get_cogs_messages
from Bot.Core.ScrimBotClient import ScrimBotClient
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestScrimBotClient(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.config = MagicMock()
        self.config.file_folder = Config().file_folder
        self.config.token = Config().token
        self.config.default_prefix = ";"
        self.context_provider = AsyncMock()
        self.guild_converter = MagicMock()
        self.game_converter = MagicMock()
        self.logger = MagicMock()
        self.logger.handler = MagicMock()
        self.client = ScrimBotClient(self.config, self.logger, self.context_provider, self.guild_converter,
                                     self.game_converter, self.loop)

    def test_setup_logging_when_called_then_discord_logger_setup(self):
        with patch("logging.getLogger", MagicMock()) as mock_logging:
            mock_logger = MagicMock()
            mock_logging.return_value = mock_logger
            self.client.setup_logging()
            calls = mock_logging.call_args_list
            self.assertEqual(calls[0], call("discord"))
            self.assertEqual(calls[1], call("sqlalchemy.engine"))
            mock_logger.addHandler.assert_called_with(self.logger.handler)
            mock_logger.setLevel.assert_called_with(DEBUG)

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

    def test_load_games_when_called_then_games_loaded_by_converter(self):
        self.config.games_dict = MagicMock()
        self.client.load_games()
        self.game_converter.init_games.assert_called_with(self.config.games_dict)

    async def test_get_prefix_when_no_guild_specific_prefix_then_default_prefix_returned(self):
        mock_bot_guild = self._mock_bot_guild_with_prefixes([])
        mock_message = MagicMock()
        mock_message.guild.id = mock_bot_guild.guild_id
        self.guild_converter.get_guild = MagicMock(return_value=mock_bot_guild)
        self.assertEqual(self.config.default_prefix, await self.client.get_prefix(mock_message))
        self.guild_converter.get_guild.assert_called_with(mock_bot_guild.guild_id)

    async def test_get_prefix_when_guild_has_one_prefix_then_guild_prefix_returned(self):
        prefixes = [f"{self.config.default_prefix}:"]
        mock_bot_guild = self._mock_bot_guild_with_prefixes(prefixes)
        mock_message = MagicMock()
        mock_message.guild.id = mock_bot_guild.guild_id
        self.guild_converter.get_guild = MagicMock(return_value=mock_bot_guild)
        self.assertEqual(prefixes, await self.client.get_prefix(mock_message))
        self.guild_converter.get_guild.assert_called_with(mock_bot_guild.guild_id)

    async def test_get_prefix_when_guild_has_multiple_prefixes_then_all_guild_prefix_returned(self):
        prefixes = ["1", "2", "3"]
        mock_bot_guild = self._mock_bot_guild_with_prefixes(prefixes)
        mock_message = MagicMock()
        mock_message.guild.id = mock_bot_guild.guild_id
        self.guild_converter.get_guild = MagicMock(return_value=mock_bot_guild)
        self.assertEqual(prefixes, await self.client.get_prefix(mock_message))
        self.guild_converter.get_guild.assert_called_with(mock_bot_guild.guild_id)

    async def test_get_deletion_time_when_no_guild_specific_time_then_default_time_returned(self):
        mock_bot_guild = self._mock_bot_guild_with_timeout(None)
        mock_discord_guild = MagicMock()
        mock_discord_guild.id = mock_bot_guild.guild_id
        self.guild_converter.get_guild = AsyncMock(return_value=mock_bot_guild)
        self.assertEqual(self.config.default_timeout, await self.client.get_deletion_time(mock_discord_guild))
        self.guild_converter.get_guild.assert_called_with(mock_bot_guild.guild_id)

    async def test_get_deletion_time_when_guild_specific_time_exists_then_guild_deletion_time_returned(self):
        guild_id = self.id_mocker.generate_viable_id()
        mock_discord_guild = MagicMock()
        mock_discord_guild.id = guild_id
        mock_bot_guild = self._mock_bot_guild_with_timeout(self.config.default_timeout + 1)
        self.guild_converter.get_guild = AsyncMock(return_value=mock_bot_guild)
        self.assertEqual(self.config.default_timeout + 1, await self.client.get_deletion_time(mock_discord_guild))
        self.guild_converter.get_guild.assert_called_with(guild_id)

    async def test_get_context_given_provider_exists_then_called_with_super_and_message(self):
        mock_message = MagicMock()
        await self.client.get_context(mock_message)
        await_args = self.context_provider.get_context.await_args
        self.assertEqual("<super: <class 'ScrimBotClient'>, <ScrimBotClient object>>", str(await_args[0][0]))
        self.assertEqual(mock_message, await_args[0][1])

    async def test_handle_exception_given_bot_exception_then_exception_resolve_called(self):
        mock_exception = AsyncMock(BotBaseException)
        mock_context = AsyncMock()
        await self.client.on_command_error(mock_context, mock_exception)
        mock_exception.resolve.assert_called_with(mock_context)

    async def test_handle_exception_given_bot_system_exception_then_exception_resolve_called(self):
        mock_exception = AsyncMock(BotBaseInternalSystemException)
        mock_context = AsyncMock()
        await self.client.on_command_error(mock_context, mock_exception)
        mock_exception.resolve.assert_called_with()

    async def test_handle_exception_given_non_bot_exception_then_exception_logged_and_raised(self):
        mock_exception = AsyncMock()
        mock_exception.__str__.return_value = "Test"
        mock_context = AsyncMock()
        await self.client.on_command_error(mock_context, mock_exception)
        self.logger.critical.assert_called_with("Test")

    async def test_invoke_given_ctx_with_command_then_super_invoke_called(self):
        mock_context = AsyncMock()
        mock_command = AsyncMock()
        mock_context.command = mock_command
        with patch("discord.ext.commands.bot.BotBase.invoke") as super_invoke:
            await self.client.invoke(mock_context)
            super_invoke.assert_called_with(mock_context)

    async def test_invoke_given_no_command_then_bot_unrecognized_command_exception_raised(self):
        mock_context = AsyncMock()
        mock_context.command = None
        mock_context.invoked_with = "faulty_command"
        expected_exception = BotUnrecognizedCommandException(mock_context)
        await self._async_assert_raises_correct_exception(expected_exception, self.client.invoke, mock_context)

    def _mock_bot_guild_with_timeout(self, timeout):
        mock_guild = MagicMock()
        mock_guild.guild_id = self.id_mocker.generate_viable_id()
        mock_guild.scrim_timeout = timeout
        return mock_guild

    def _mock_bot_guild_with_prefixes(self, prefixes):
        mock_guild = MagicMock()
        mock_guild.guild_id = self.id_mocker.generate_viable_id()
        mock_guild.prefixes = prefixes
        return mock_guild
