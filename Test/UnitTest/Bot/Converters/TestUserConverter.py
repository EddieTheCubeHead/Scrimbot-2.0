__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch, AsyncMock

from discord.ext.commands import MemberNotFound

from Bot.Converters.UserConverter import UserConverter
from Bot.DataClasses.User import User
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
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
        mock_user.id = self.id_mocker.generate_viable_id()
        self.connection.get_user.return_value = mock_user
        self.discord_convert.return_value = mock_user
        with patch("discord.ext.commands.converter.MemberConverter.convert", self.discord_convert):
            actual_user = await self.converter.convert(self.context, str(mock_user.id))
        self.assertEqual(mock_user, actual_user)
        self.connection.get_user.assert_called_with(mock_user.id)

    async def test_convert_when_called_then_discord_member_added_to_the_user(self):
        mock_user = MagicMock()
        mock_discord_member = MagicMock()
        mock_discord_member.id = self.id_mocker.generate_viable_id()
        self.discord_convert.return_value = mock_discord_member
        with patch("discord.ext.commands.converter.MemberConverter.convert", self.discord_convert):
            actual_user = await self.converter.convert(self.context, str(mock_user.id))
        self.assertEqual(mock_discord_member, actual_user.member)
        self.connection.get_user.assert_called_with(mock_discord_member.id)

    async def test_convert_given_discord_member_not_found_then_exception_caught_and_bot_exception_thrown(self):
        mock_user = MagicMock()
        mock_discord_member = MagicMock()
        mock_discord_member.id = self.id_mocker.generate_viable_id()
        self.discord_convert.side_effect = MemberNotFound(str(mock_user.id))
        reason = "argument is not a valid username, nickname, user id or mention on this server"
        expected_exception = BotConversionFailureException(User.__name__, str(mock_user.id), reason=reason)
        with patch("discord.ext.commands.converter.MemberConverter.convert", self.discord_convert):
            await self._async_assert_raises_correct_exception(expected_exception, self.converter.convert, self.context,
                                                              str(mock_user.id))

    def test_get_user_given_called_with_user_id_then_user_returned(self):
        mock_user = MagicMock()
        mock_user.id = self.id_mocker.generate_viable_id()
        self.connection.get_user.return_value = mock_user
        actual_user = self.converter.get_user(mock_user.id)
        self.assertEqual(mock_user, actual_user)
        self.connection.get_user.assert_called_with(mock_user.id)

    def test_is_in_scrim_given_user_not_in_scrim_when_called_with_user_id_then_false_returned(self):
        self.connection.is_in_scrim.return_value = False
        mock_user = MagicMock()
        self.assertFalse(self.converter.is_in_scrim(mock_user))
        self.connection.is_in_scrim.assert_called_with(mock_user.user_id)

    def test_is_in_scrim_given_user_in_scrim_when_called_with_user_id_then_true_returned(self):
        self.connection.is_in_scrim.return_value = True
        mock_user = MagicMock()
        self.assertTrue(self.converter.is_in_scrim(mock_user))
        self.connection.is_in_scrim.assert_called_with(mock_user.user_id)
