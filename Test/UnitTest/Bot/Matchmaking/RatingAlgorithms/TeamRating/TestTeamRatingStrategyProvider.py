__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategyProvider import TeamRatingStrategyProvider
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.test_utils import create_mock_strategy


class TestTeamRatingStrategyProvider(UnittestBase):

    def setUp(self) -> None:
        self.mean_strategy = create_mock_strategy("mean")
        self.weighted_best_player_strategy = create_mock_strategy("weighted_best")
        self.provider = TeamRatingStrategyProvider(self.mean_strategy, self.weighted_best_player_strategy)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(TeamRatingStrategyProvider)

    def test_get_strategy_given_mean_argument_then_returns_mean_strategy(self):
        self.assertEqual(self.mean_strategy, self.provider.get_strategy("mean"))

    def test_get_strategy_given_weighted_best_argument_then_returns_weighted_best_strategy(self):
        self.assertEqual(self.weighted_best_player_strategy, self.provider.get_strategy("weighted_best"))

    def test_get_strategy_given_invalid_argument_then_returns_mean_strategy(self):
        self.assertEqual(self.mean_strategy, self.provider.get_strategy("invalid"))
