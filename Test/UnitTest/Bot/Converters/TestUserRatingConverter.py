__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.UserRatingConverter import UserRatingConverter
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestUserRatingConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.context = MagicMock()
        self.converter = UserRatingConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserRatingConverter)

    def test_get_rating_given_user_game_and_guild_then_calls_connection_with_ids_and_returns_result(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        self.connection.get_user_rating.return_value = mock_rating
        actual = self.converter.get_user_rating(mock_user, mock_game, mock_guild)
        self.assertEqual(mock_rating, actual)
        self.connection.get_user_rating.assert_called_with(mock_user.user_id, mock_game.name, mock_guild.guild_id)

    def test_set_rating_given_user_game_guild_and_rating_then_calls_connection_with_ids_and_returns_rating(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        self.connection.set_user_rating.return_value = mock_rating
        actual = self.converter.set_user_rating(4321, mock_user, mock_game, mock_guild)
        self.assertEqual(mock_rating, actual)
        self.connection.set_user_rating.assert_called_with(4321, mock_user.user_id, mock_game.name, mock_guild.guild_id)

    def _create_mock_user(self):
        mock_user = MagicMock()
        mock_user.user_id = self.id_mocker.generate_viable_id()
        return mock_user

    def _create_mock_game(self):
        mock_game = MagicMock()
        mock_game.name = str(self.id_mocker.generate_viable_id())
        return mock_game

    def _create_mock_guild(self):
        mock_guild = MagicMock()
        mock_guild.guild_id = self.id_mocker.generate_viable_id()
        return mock_guild
