__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch, AsyncMock

from Bot.Converters.UserConverter import UserConverter
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestUserConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.discord_convert = AsyncMock()
        self.connection = MagicMock()
        self.context = MagicMock()
        self.converter = UserConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserConverter)

    async def test_convert_given_called_with_new_user_then_discord_converter_called_and_new_user_returned(self):
        mock_user = MagicMock()
        mock_discord_member = MagicMock()
        mock_discord_member.id = self.id_mocker.generate_viable_id()
        mock_user.id = self.id_mocker.generate_viable_id()
        self.connection.get_user.return_value = mock_user
        self.discord_convert.return_value = mock_discord_member
        with patch("discord.ext.commands.converter.MemberConverter.convert", self.discord_convert):
            actual_user = await self.converter.convert(self.context, str(mock_user.id))
        self.assertEqual(mock_user, actual_user)
        self.assertEqual(mock_discord_member, actual_user.member)
        self.connection.get_user.assert_called_with(mock_discord_member.id)

    def test_get_user_given_called_with_user_id_then_user_returned(self):
        mock_user = MagicMock()
        mock_user.id = self.id_mocker.generate_viable_id()
        self.connection.get_user.return_value = mock_user
        actual_user = self.converter.get_user(mock_user.id)
        self.assertEqual(mock_user, actual_user)
        self.connection.get_user.assert_called_with(mock_user.id)
