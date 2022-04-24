__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Cogs.Helpers.BotSettingsService import BotSettingsService
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotSettingsService(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.config = MagicMock()
        self.guild_converter = MagicMock()
        self.client = BotSettingsService(self.config, self.guild_converter)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(BotSettingsService)

    def test_get_deletion_time_when_no_guild_specific_time_then_default_time_returned(self):
        mock_bot_guild = self._mock_bot_guild_with_timeout(None)
        mock_discord_guild = MagicMock()
        mock_discord_guild.id = mock_bot_guild.guild_id
        self.guild_converter.get_guild = MagicMock(return_value=mock_bot_guild)
        self.assertEqual(self.config.default_timeout, self.client.get_deletion_time(mock_discord_guild))
        self.guild_converter.get_guild.assert_called_with(mock_bot_guild.guild_id)

    def test_get_deletion_time_when_guild_specific_time_exists_then_guild_deletion_time_returned(self):
        guild_id = self.id_generator.generate_viable_id()
        mock_discord_guild = MagicMock()
        mock_discord_guild.id = guild_id
        mock_bot_guild = self._mock_bot_guild_with_timeout(self.config.default_timeout + 1)
        self.guild_converter.get_guild = MagicMock(return_value=mock_bot_guild)
        self.assertEqual(self.config.default_timeout + 1, self.client.get_deletion_time(mock_discord_guild))
        self.guild_converter.get_guild.assert_called_with(guild_id)

    def _mock_bot_guild_with_timeout(self, timeout):
        mock_guild = MagicMock()
        mock_guild.guild_id = self.id_generator.generate_viable_id()
        mock_guild.scrim_timeout = timeout
        return mock_guild
