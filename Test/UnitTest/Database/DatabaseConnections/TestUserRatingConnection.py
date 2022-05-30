__version__ = "ver"
__author__ = "Eetu Asikainen"

from typing import Optional
from unittest.mock import MagicMock

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.DataClasses.UserRating import UserRating, DEFAULT_RATING
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.UserRatingConnection import UserRatingConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_results(wins: int, losses: int):
    return [True for _ in range(wins)] + [False for _ in range(losses)]


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

    def test_get_user_statistics_when_called_then_user_and_matches_joined(self):
        expected_user_rating = self._create_user_rating(2345)
        results = _create_results(12, 7)
        self._create_scrims(expected_user_rating.user, expected_user_rating.game, *results)
        actual_user_rating = self.connection.get_user_statistics(expected_user_rating.user, expected_user_rating.game,
                                                                 expected_user_rating.guild)
        self._assert_results(12, 7, actual_user_rating)

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

    def _assert_results(self, expected_wins: int, expected_losses: int, rating: UserRating):
        wins, losses = 0, 0
        checked_scrims = []
        all_scrims = [scrim for team in rating.user.teams for scrim in team.scrims]
        for scrim_team in all_scrims:
            if scrim_team.placement == 1:
                wins += 1
            else:
                losses += 1
            checked_scrims.append(scrim_team)
        self.assertEqual(expected_wins, wins, f"Expected teams '{checked_scrims}' to contain {expected_wins} wins, but "
                                              f"found {wins} wins")
        self.assertEqual(expected_wins, wins, f"Expected teams '{checked_scrims}' to contain {expected_losses} losses, "
                                              f"but found {losses} losses")

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

    def _create_scrims(self, user: User, game: Game, *results: bool):
        for result in results:
            new_scrim = self._create_scrim(game)
            new_team = self._create_team(user, game)
            participant_team = ParticipantTeam(1 if result else 2)
            participant_team.team = new_team
            participant_team.scrim = new_scrim
            with self.master.get_session() as session:
                session.add(participant_team)

    def _create_scrim(self, game: Game):
        mock_manager = MagicMock()
        mock_manager.message.channel.id = self.id_generator.generate_viable_id()
        mock_manager.teams_manager.game = game
        scrim = Scrim(mock_manager)
        with self.master.get_session() as session:
            session.add(scrim)
        return scrim

    def _create_team(self, user: User, game: Game):
        players = [User(self.id_generator.generate_viable_id()) for _ in range(1, game.min_team_size)]
        players.append(user)
        team = Team(str(self.id_generator.generate_viable_id()), players, game.min_team_size, game.max_team_size)
        with self.master.get_session() as session:
            session.add(team)
        return team
