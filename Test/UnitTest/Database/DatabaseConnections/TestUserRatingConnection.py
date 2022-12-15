__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from typing import Optional
from unittest.mock import MagicMock

from Src.Bot.DataClasses.UserScrimResult import Result, UserScrimResult
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Guild import Guild
from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.Team import Team
from Src.Bot.DataClasses.User import User
from Src.Bot.DataClasses.UserRating import UserRating, DEFAULT_RATING
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.UserRatingConnection import UserRatingConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_result_list(wins: int, losses: int, ties: int = 0, unregistered: int = 0):
    return [Result.WIN for _ in range(wins)] + [Result.LOSS for _ in range(losses)] + [Result.TIE for _ in range(ties)]\
           + [Result.UNREGISTERED for _ in range(unregistered)]


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

    def test_get_user_rating_given_user_exists_when_game_guild_and_user_id_given_then_user_rating_returned(self):
        expected_user_rating = self._create_user_rating(1234)
        with self.master.get_session() as session:
            session.add(expected_user_rating)
        actual_user_rating = self.connection.get_user_rating(expected_user_rating.user,
                                                             expected_user_rating.game,
                                                             expected_user_rating.guild)
        self._assert_equal_ratings(expected_user_rating, actual_user_rating)

    def test_get_user_rating_given_user_does_not_exist_when_user_queried_then_default_rating_set(self):
        mock_game = self._create_game()
        mock_guild = self._create_guild()
        mock_user = self._create_user()
        actual_user_rating = self.connection.get_user_rating(mock_user, mock_game, mock_guild)
        self.assertEqual(DEFAULT_RATING, actual_user_rating.rating)
        self.assertEqual(mock_user, actual_user_rating.user)
        self.assertEqual(mock_game, actual_user_rating.game)
        self.assertEqual(mock_guild, actual_user_rating.guild)

    @unittest.skip("Waiting for scrim handling rewrite")
    def test_get_user_statistics_when_called_then_user_game_and_matches_joined(self):
        expected_user_rating = self._create_user_rating(2345)
        results = _create_result_list(12, 7)
        self._create_results(expected_user_rating, *results)
        actual_user_rating = self.connection.get_user_statistics(expected_user_rating.user, expected_user_rating.game,
                                                                 expected_user_rating.guild)
        self.assertEqual(expected_user_rating.game.name, actual_user_rating.game.name)
        self._assert_results(actual_user_rating, 12, 7)

    def test_set_rating_when_given_valid_user_guild_game_and_rating_then_new_rating_created_and_returned(self):
        mock_game = self._create_game()
        mock_user = self._create_user()
        mock_guild = self._create_guild()
        actual_user_rating = self.connection.set_user_rating(2222, mock_user, mock_game, mock_guild)
        self.assertEqual(mock_user, actual_user_rating.user)
        self.assertEqual(mock_game, actual_user_rating.game)
        self.assertEqual(mock_guild, actual_user_rating.guild)
        self.assertEqual(2222, actual_user_rating.rating)

    def test_set_rating_given_existing_user_then_rating_set_and_user_returned(self):
        expected_user_rating = self._create_user_rating(1234)
        with self.master.get_session() as session:
            session.add(expected_user_rating)
        actual_user_rating = self.connection.set_user_rating(4424,
                                                             expected_user_rating.user,
                                                             expected_user_rating.game,
                                                             expected_user_rating.guild)
        expected_user_rating.rating = 4424
        self._assert_equal_ratings(expected_user_rating, actual_user_rating)

    @unittest.skip("Waiting for scrim handling rewrite")
    def test_get_rating_given_existing_results_when_new_rating_created_then_results_linked(self):
        expected_user_rating = MagicMock()
        expected_user_rating.game = self._create_game()
        expected_user_rating.user = self._create_user()
        expected_user_rating.guild = self._create_guild()
        expected_user_rating.rating_id = None
        results = _create_result_list(12, 7)
        self._create_results(expected_user_rating, *results)
        actual_user_rating = self.connection.get_user_rating(expected_user_rating.user, expected_user_rating.game,
                                                             expected_user_rating.guild)
        self.assertEqual(expected_user_rating.game.name, actual_user_rating.game.name)
        self._assert_results(actual_user_rating, 12, 7)

    def _assert_results(self, rating: UserRating, expected_wins: int, expected_losses: int, expected_ties: int = 0,
                        expected_unregistered: int = 0):
        wins = len(list(filter(lambda x: x.result == Result.WIN, rating.results)))
        losses = len(list(filter(lambda x: x.result == Result.LOSS, rating.results)))
        ties = len(list(filter(lambda x: x.result == Result.TIE, rating.results)))
        unrecorded = len(list(filter(lambda x: x.result == Result.UNREGISTERED, rating.results)))
        self.assertEqual(expected_wins, wins)
        self.assertEqual(expected_losses, losses)
        self.assertEqual(expected_ties, ties)
        self.assertEqual(expected_unregistered, unrecorded)

    def _create_user_rating(self, user_rating: Optional[int] = None) -> UserRating:
        mock_game = self._create_game()
        mock_user = self._create_user()
        mock_guild = self._create_guild()
        mock_user_rating = UserRating(mock_user.user_id, mock_game.name, mock_guild.guild_id, user_rating)
        mock_user_rating.user = mock_user
        mock_user_rating.game = mock_game
        mock_user_rating.guild = mock_guild
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

    def _create_scrim(self, game: Game):
        mock_manager = MagicMock()
        mock_manager.message.channel.id = self.id_generator.generate_viable_id()
        mock_manager.teams_manager.game = game
        scrim = Scrim(mock_manager)
        with self.master.get_session() as session:
            session.add(scrim)
        return scrim

    def _create_results(self, rating: UserRating, *results: Result):
        for result in results:
            new_scrim = self._create_scrim(rating.game)
            new_result = UserScrimResult(rating.user.user_id, rating.rating_id, new_scrim.scrim_id, DEFAULT_RATING,
                                         result)
            with self.master.get_session() as session:
                session.add(new_result)
