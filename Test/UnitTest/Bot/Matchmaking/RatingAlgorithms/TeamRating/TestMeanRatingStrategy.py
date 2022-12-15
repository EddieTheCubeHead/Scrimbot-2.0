__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Src.Bot.Matchmaking.RatingAlgorithms.TeamRating.MeanRatingStrategy import MeanRatingStrategy
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.test_utils import create_team_from_ratings


class TestMeanRatingStrategy(UnittestBase):

    def setUp(self) -> None:
        self.strategy = MeanRatingStrategy()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(MeanRatingStrategy)

    def test_get_rating_given_five_identical_ratings_rating_equal_to_all_five(self):
        rating = 30
        ratings = create_team_from_ratings(rating, rating, rating, rating, rating)
        self.assertEqual(rating, self.strategy.get_rating(*ratings))

    def test_get_rating_given_different_ratings_then_the_mean_returned(self):
        ratings = create_team_from_ratings(30, 10, 50, 70, 90)
        self.assertEqual(50, self.strategy.get_rating(*ratings))

    def test_get_name_returns_mean(self):
        self.assertEqual("mean", self.strategy.name)
