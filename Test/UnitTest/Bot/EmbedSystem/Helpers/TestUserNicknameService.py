__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import patch, MagicMock

from Bot.EmbedSystem.Helpers.UserNicknameService import UserNicknameService
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestUserNicknameService(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.service = UserNicknameService()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserNicknameService)

    def test_get_name_given_context_and_user_id_then_nickname_fetched(self):
        with patch("discord.utils.get") as mock_get:
            mock_member = MagicMock()
            mock_member.display_name = "Test_nick"
            mock_get.return_value = mock_member
            mock_id = self.id_generator.generate_viable_id()
            mock_guild = MagicMock()
            actual_name = self.service.get_name(mock_guild, mock_id)
            self.assertEqual(mock_member.display_name, actual_name)

    def test_get_name_is_cached(self):
        with patch("discord.utils.get") as mock_get:
            mock_member = MagicMock()
            mock_member.display_name = "Test_nick"
            mock_get.return_value = mock_member
            mock_id = self.id_generator.generate_viable_id()
            mock_guild = MagicMock()
            self.service.get_name(mock_guild, mock_id)
            self.service.get_name(mock_guild, mock_id)
            mock_get.assert_called_once()


