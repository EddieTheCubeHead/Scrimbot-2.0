__version__ = "ver"
__author__ = "Eetu Asikainen"

from typing import Optional
from unittest.mock import MagicMock

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.User import User
from Bot.DataClasses.UserRating import UserRating, DEFAULT_RATING
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.UserRatingConnection import UserRatingConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestUserRatingConnection(UnittestBase):

    config: Optional[Config] = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = Config()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection = UserRatingConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserRatingConnection)

    def test_get_rating_given_user_exists_when_game_guild_and_user_id_given_then_user_rating_returned(self):
        expected_user_rating = self._create_user_rating(1234)
        with self.master.get_session() as session:
            session.add(expected_user_rating)
        actual_user_rating = self.connection.get_user_rating(expected_user_rating.user_id,
                                                             expected_user_rating.game_name,
                                                             expected_user_rating.guild_id)
        self._assert_equal_ratings(expected_user_rating, actual_user_rating)

    def test_get_rating_given_user_does_not_exist_when_user_queried_then_default_rating_set(self):
        actual_user_rating = self.connection.get_user_rating(*self.id_generator.generate_viable_id_group(3))
        self.assertEqual(DEFAULT_RATING, actual_user_rating.rating)

    def test_set_rating_when_given_valid_user_guild_game_and_rating_then_new_rating_created_and_returned(self):
        expected_user_rating = self._create_user_rating(2233)
        actual_user_rating = self.connection.set_user_rating(expected_user_rating.rating,
                                                             expected_user_rating.user_id,
                                                             expected_user_rating.game_name,
                                                             expected_user_rating.guild_id)
        self._assert_equal_ratings(expected_user_rating, actual_user_rating)

    def test_set_rating_given_existing_user_then_rating_set_and_user_returned(self):
        expected_user_rating = self._create_user_rating(1234)
        with self.master.get_session() as session:
            session.add(expected_user_rating)
        actual_user_rating = self.connection.set_user_rating(4424,
                                                             expected_user_rating.user_id,
                                                             expected_user_rating.game_name,
                                                             expected_user_rating.guild_id)
        expected_user_rating.rating = 4424
        self._assert_equal_ratings(expected_user_rating, actual_user_rating)

    def _create_user_rating(self, user_rating: Optional[int] = None) -> UserRating:
        mock_game = self._create_game()
        mock_user = self._create_user()
        mock_guild = self._create_guild()
        mock_user_rating = UserRating(mock_user.user_id, mock_game.name, mock_guild.guild_id, user_rating)
        return mock_user_rating

    def _create_game(self) -> Game:
        return Game(str(self.id_generator.generate_viable_id()), "colour", "icon", 5)

    def _create_user(self) -> User:
        return User(self.id_generator.generate_viable_id())

    def _create_guild(self) -> Guild:
        return Guild(self.id_generator.generate_viable_id())

    def _assert_equal_ratings(self, expected_user_rating, actual_user_rating):
        self.assertEqual(expected_user_rating.user_id, actual_user_rating.user_id)
        self.assertEqual(expected_user_rating.game_name, actual_user_rating.game_name)
        self.assertEqual(expected_user_rating.guild_id, actual_user_rating.guild_id)
        self.assertEqual(expected_user_rating.rating, actual_user_rating.rating)
