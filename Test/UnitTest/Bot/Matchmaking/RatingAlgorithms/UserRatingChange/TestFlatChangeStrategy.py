__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import Result
from Src.Bot.Matchmaking.RatingAlgorithms.UserRatingChange.FlatChangeStrategy import FlatChangeStrategy
from Utils.TestBases.UnittestBase import UnittestBase


class TestFlatChangeStrategy(UnittestBase):

    def setUp(self) -> None:
        self.strategy = FlatChangeStrategy()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(FlatChangeStrategy)

    def test_get_rating_when_winning_returns_positive_flat_change(self):
        mock_user_rating = self._create_mock_user_rating()
        self.assertEqual(25, self.strategy.get_rating_change(mock_user_rating, Result.WIN, 3421, 1111))

    def test_get_rating_when_losing_returns_negative_flat_change(self):
        mock_user_rating = self._create_mock_user_rating()
        self.assertEqual(-25, self.strategy.get_rating_change(mock_user_rating, Result.LOSS, 5421, 11))

    def test_get_rating_when_tying_returns_zero(self):
        mock_user_rating = self._create_mock_user_rating()
        self.assertEqual(0, self.strategy.get_rating_change(mock_user_rating, Result.TIE, 32, 5896))

    @staticmethod
    def _create_mock_user_rating(rating: int = 1700) -> UserRating:
        mock_rating = MagicMock()
        mock_rating.rating = rating
        return mock_rating
