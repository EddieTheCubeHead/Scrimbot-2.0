__version__ = "0.1"
__author__ = "Eetu Asikainen"

from math import sqrt

from Src.Bot.Matchmaking.RatingAlgorithms.TeamRating.WeightBestPlayerRatingStrategy import WeightBestPlayerRatingStrategy
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.test_utils import create_team_from_ratings


class TestWeightBestPlayerRatingStrategy(UnittestBase):

    def setUp(self) -> None:
        self.strategy = WeightBestPlayerRatingStrategy()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(WeightBestPlayerRatingStrategy)

    def test_get_rating_given_five_identical_ratings_rating_equal_to_all_five(self):
        rating = 30
        ratings = create_team_from_ratings(rating, rating, rating, rating, rating)
        self.assertEqual(rating, self.strategy.get_rating(*ratings))

    def test_get_rating_given_different_ratings_then_the_mean_returned(self):
        ratings = [30, 10, 50, 70, 90]
        rating_team = create_team_from_ratings(*ratings)
        expected_team_rating = (sum(ratings) + sqrt((sum(ratings) / len(ratings)) * max(ratings))) / (len(ratings) + 1)
        self.assertEqual(expected_team_rating, self.strategy.get_rating(*rating_team))
