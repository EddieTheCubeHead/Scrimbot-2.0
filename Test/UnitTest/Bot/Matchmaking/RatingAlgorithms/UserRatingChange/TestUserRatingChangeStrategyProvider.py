__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Matchmaking.RatingAlgorithms.UserRatingChange.UserRatingChangeStrategyProvider import UserRatingChangeStrategyProvider
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.test_utils import create_mock_strategy


class TestUserRatingChangeStrategyProvider(UnittestBase):

    def setUp(self) -> None:
        self.flat_change_strategy = create_mock_strategy("flat")
        self.provider = UserRatingChangeStrategyProvider(self.flat_change_strategy)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserRatingChangeStrategyProvider)

    def test_get_strategy_given_flat_change_argument_then_returns_flat_change_strategy(self):
        self.assertEqual(self.flat_change_strategy, self.provider.get_strategy("flat"))

    def test_get_strategy_given_invalid_argument_then_returns_flat_change_strategy(self):
        self.assertEqual(self.flat_change_strategy, self.provider.get_strategy("invalid"))
