__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.UserRatingConverter import UserRatingConverter
from Bot.DataClasses.UserScrimResult import Result
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

    def test_get_user_rating_given_user_game_and_guild_then_calls_connection_with_ids_and_returns_result(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        self.connection.get_user_rating.return_value = mock_rating
        actual = self.converter.get_user_rating(mock_user, mock_game, mock_guild)
        self.assertEqual(mock_rating, actual)
        self.connection.get_user_rating.assert_called_with(mock_user, mock_game, mock_guild)

    def test_get_user_statistics_given_user_game_and_guild_then_calls_connection_with_ids_and_returns_result(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        self.connection.get_user_statistics.return_value = mock_rating
        actual = self.converter.get_user_statistics(mock_user, mock_game, mock_guild)
        self.assertEqual(mock_rating, actual)
        self.connection.get_user_statistics.assert_called_with(mock_user, mock_game, mock_guild)

    def test_get_user_statistics_given_member_attached_to_user_then_member_set_to_rating_user(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_member = MagicMock()
        mock_user.member = mock_member
        mock_rating = MagicMock()
        self.connection.get_user_statistics.return_value = mock_rating
        actual = self.converter.get_user_statistics(mock_user, mock_game, mock_guild)
        self.assertEqual(mock_member, actual.user.member)

    def test_set_user_rating_given_user_game_guild_and_rating_then_calls_connection_with_ids_and_returns_rating(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        self.connection.set_user_rating.return_value = mock_rating
        actual = self.converter.set_user_rating(4321, mock_user, mock_game, mock_guild)
        self.assertEqual(mock_rating, actual)
        self.connection.set_user_rating.assert_called_with(4321, mock_user, mock_game, mock_guild)

    def test_create_user_rating_given_user_game_guild_and_rating_then_statistics_fetched(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        self.connection.set_user_rating.return_value = MagicMock()
        self.connection.get_user_statistics.return_value = mock_rating
        actual = self.converter.create_user_rating(4321, mock_user, mock_game, mock_guild)
        self.assertEqual(mock_rating, actual)
        self.connection.set_user_rating.assert_called_with(4321, mock_user, mock_game, mock_guild)
        self.connection.get_user_statistics.assert_called_with(mock_user, mock_game, mock_guild)

    def test_create_user_rating_given_member_attached_to_user_then_member_set_to_rating_user(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_rating = MagicMock()
        mock_member = MagicMock()
        mock_user.member = mock_member
        self.connection.set_user_rating.return_value = MagicMock()
        self.connection.get_user_statistics.return_value = mock_rating
        actual = self.converter.create_user_rating(4321, mock_user, mock_game, mock_guild)
        self.assertEqual(mock_member, actual.user.member)

    def test_update_user_rating_given_called_then_user_rating_fetched_and_updated_and_user_scrim_result_created(self):
        mock_user = self._create_mock_user()
        mock_game = self._create_mock_game()
        mock_guild = self._create_mock_guild()
        mock_original_rating = MagicMock()
        mock_original_rating.rating = 1234
        mock_member = MagicMock()
        mock_user.member = mock_member
        mock_updated_rating = MagicMock()
        self.connection.get_user_rating.return_value = mock_original_rating
        self.connection.set_user_rating.return_value = mock_updated_rating
        self.converter.update_user_rating(10, mock_user, mock_game, mock_guild)
        self.connection.set_user_rating.assert_called_with(1244, mock_user, mock_game, mock_guild)

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
