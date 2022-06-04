__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.GuildMember import GuildMember, PermissionLevel
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.GuildMemberConnection import GuildMemberConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestGuildMemberConnection(UnittestBase):

    config: Config = None
    master: MasterConnection = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = MagicMock()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection: GuildMemberConnection = GuildMemberConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(GuildMemberConnection)

    def test_get_guild_member_given_member_does_not_exist_then_new_member_created_and_perms_set_to_none(self):
        mock_user = self._create_mock_user()
        mock_guild = self._create_mock_guild()
        actual = self.connection.get_guild_member(mock_user.user_id, mock_guild.guild_id)
        self._assert_exists(actual)
        self.assertEqual(PermissionLevel.NONE, actual.bot_guild_rights_level)

    def test_get_guild_member_given_member_exists_then_member_fetched(self):
        mock_user = self._create_mock_user()
        mock_guild = self._create_mock_guild()
        expected = GuildMember(mock_user.user_id, mock_guild.guild_id)
        expected.bot_guild_rights_level = PermissionLevel.BOT_ADMIN
        with self.master.get_session() as session:
            session.add(expected)
        actual = self.connection.get_guild_member(mock_user.user_id, mock_guild.guild_id)
        self.assertEqual(PermissionLevel.BOT_ADMIN, actual.bot_guild_rights_level)


    def _create_mock_guild(self):
        mock_guild = MagicMock()
        mock_guild.guild_id = self.id_generator.generate_viable_id()
        return mock_guild

    def _create_mock_user(self):
        mock_user = MagicMock()
        mock_user.user_id = self.id_generator.generate_viable_id()
        return mock_user

    def _assert_exists(self, actual: GuildMember):
        with self.master.get_session() as session:
            expected = session.query(GuildMember).filter(GuildMember.guild_id == actual.guild_id) \
                .filter(GuildMember.user_id == actual.user_id).first()
        self.assertIsNotNone(expected)
        self.assertEqual(expected.bot_guild_rights_level, actual.bot_guild_rights_level)

