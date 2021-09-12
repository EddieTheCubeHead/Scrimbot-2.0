__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.TestIdGenerator import TestIdGenerator
from Utils.UnittestBase import UnittestBase
from Bot.Converters.GuildConverter import GuildConverter


class TestGuildConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.converter = GuildConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(GuildConverter)

    def test_convert_given_string_then_connection_called_with_int_version(self):
        guild_id = self.id_mocker.generate_viable_id()
        self.converter.convert(str(guild_id))
        self.connection.get_guild.assert_called_with(guild_id)

    def test_get_guild_given_id_then_connection_called(self):
        guild_id = self.id_mocker.generate_viable_id()
        self.converter.get_guild(guild_id)
        self.connection.get_guild.assert_called_with(guild_id)

    def test_get_guild_given_called_twice_then_cache_utilized_and_connection_called_once(self):
        guild_id = self.id_mocker.generate_viable_id()
        self.converter.get_guild(guild_id)
        self.converter.get_guild(guild_id)
        self.connection.get_guild.assert_called_once()
