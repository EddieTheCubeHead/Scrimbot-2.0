__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.Prefix import Prefix
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Utils.TestBases.UnittestBase import UnittestBase
from Database.DatabaseConnections.GuildConnection import GuildConnection


def _construct_prefixes(*prefixes):
    constructed = []
    for prefix in prefixes:
        constructed.append(Prefix(prefix=prefix))
    return constructed


class TestGuildConnection(UnittestBase):

    config: Config = None
    master: MasterConnection = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = MagicMock()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection: GuildConnection = GuildConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(GuildConnection)

    def test_get_guild_given_existing_id_then_guild_returned(self):
        guild_id = self.id_generator.generate_viable_id()
        mock_guild = Guild(guild_id=guild_id)
        with self.master.get_session() as session:
            session.add(mock_guild)
            session.commit()
        actual = self.connection.get_guild(guild_id)
        self.assertEqual(guild_id, actual.guild_id)

    def test_get_guild_given_existing_id_with_prefixes_then_prefixes_returned(self):
        guild_id = self.id_generator.generate_viable_id()
        prefixes = _construct_prefixes("//", ";", "s?")
        mock_guild = Guild(guild_id=guild_id, prefixes=prefixes)
        with self.master.get_session() as session:
            
            session.add(mock_guild)
        actual = self.connection.get_guild(guild_id)
        self._assert_equal_prefixes(prefixes, actual.prefixes)

    def test_get_guild_given_guild_does_not_exist_then_guild_created_returned_and_inserted_to_database(self):
        new_guild_id = self.id_generator.generate_viable_id()
        new_guild = self.connection.get_guild(new_guild_id)
        self.assertEqual(new_guild_id, new_guild.guild_id)
        self._assert_guild_in_database(new_guild_id)

    def test_get_guild_given_guild_does_not_exist_then_returned_guild_has_prefix_data(self):
        new_guild_id = self.id_generator.generate_viable_id()
        new_guild = self.connection.get_guild(new_guild_id)
        self.assertEqual([], new_guild.prefixes)

    def _assert_guild_in_database(self, guild_id):
        with self.master.get_session() as session:
            session.query(Guild).filter(Guild.guild_id == guild_id).one()

    def _assert_equal_prefixes(self, actual_prefixes, expected_prefixes):
        for actual, expected in zip(actual_prefixes, expected_prefixes):
            self.assertEqual(actual.prefix, expected.prefix)
