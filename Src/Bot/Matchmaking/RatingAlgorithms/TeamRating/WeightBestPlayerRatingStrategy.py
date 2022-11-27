__version__ = "0.1"
__author__ = "Eetu Asikainen"

from math import sqrt

from hintedi import HinteDI

from Bot.DataClasses.UserRating import UserRating
from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategy import TeamRatingStrategy


@HinteDI.singleton_implementation(base=TeamRatingStrategy, key='weighted_best', is_default=True)
class WeightBestPlayerRatingStrategy(TeamRatingStrategy):

    def get_rating(self, *member_ratings: UserRating) -> float:
        ratings = [member.rating for member in member_ratings]
        return (sum(ratings) + sqrt((sum(ratings) / len(ratings)) * max(ratings))) / (len(ratings) + 1)
