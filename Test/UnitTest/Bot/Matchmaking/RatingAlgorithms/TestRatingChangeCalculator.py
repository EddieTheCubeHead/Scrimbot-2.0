__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.Team import Team
from Bot.DataClasses.UserScrimResult import Result
from Bot.Matchmaking.RatingAlgorithms.RatingChangeCalculator import RatingChangeCalculator
from Utils.TestBases.UnittestBase import UnittestBase


class TestRatingChangeCalculator(UnittestBase):

    def setUp(self) -> None:
        self.user_rating_change_strategy_provider = MagicMock()
        self.team_rating_strategy_provider = MagicMock()
        self.rating_converter = MagicMock()
        self.rating_converter.get_user_rating.return_value = MagicMock()
        self.calculator = RatingChangeCalculator(self.user_rating_change_strategy_provider,
                                                 self.team_rating_strategy_provider, self.rating_converter)
        self.user_rating_change_strategy = MagicMock()
        self.user_rating_change_strategy_provider.get_strategy.return_value = self.user_rating_change_strategy
        self.team_rating_strategy = MagicMock()
        self.team_rating_strategy_provider.get_strategy.return_value = self.team_rating_strategy
        self.mock_game = MagicMock()
        self.mock_guild = MagicMock()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(RatingChangeCalculator)

    def test_when_using_flat_rating_change_strategy_in_two_team_scrim_then_ratings_modified_by_flat_amounts(self):
        result = self._create_results(self.mock_game, self.mock_guild, ("Team 1",), ("Team 2",))
        self.user_rating_change_strategy.get_rating_change = lambda _, x, __, ___: 25 if x == Result.WIN else -25
        changes = self.calculator.calculate_changes(self.mock_game, self.mock_guild, result)
        for player in result[0][0].members:
            self.assertEqual(25, changes[player])
        for player in result[1][0].members:
            self.assertEqual(-25, changes[player])

    def _create_results(self, game: Game, guild: Guild, *team_groups: tuple[str, ...]) -> ScrimResult:
        result_list = []
        for team_group in team_groups:
            result_list.append(self._create_result_group(game, guild, team_group))
        return result_list

    def _create_result_group(self, game: Game, guild: Guild, result_group: tuple[str, ...]) -> tuple[Team]:
        teams = []
        for team_name in result_group:
            mocked_team = self._create_mock_team(game, guild, team_name)
            teams.append(mocked_team)
        return tuple(teams)

    def _create_mock_team(self, game: Game, guild: Guild, name: str, size: int = 5) -> Team:
        mock_team = Team(name)
        players = []
        for _ in range(size):
            players.append(self._create_player_with_rating(game, guild))
        mock_team.members = players
        return mock_team

    @staticmethod
    def _create_player_with_rating(game: Game, guild: Guild):
        player = MagicMock()
        player.ratings = []
        rating = MagicMock()
        rating.game_name = game.name
        rating.guild_id = guild.guild_id
        player.ratings.append(rating)
        return player

