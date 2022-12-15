__version__ = "0.1"
__author__ = "Eetu Asikainen"

from statistics import mean

from hintedi import HinteDI

from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategy import TeamRatingStrategy


@HinteDI.singleton_implementation(base=TeamRatingStrategy, key='mean')
class MeanRatingStrategy(TeamRatingStrategy):

    def get_rating(self, *member_ratings: UserRating) -> float:
        return mean([member_rating.rating for member_rating in member_ratings])

    @property
    def name(self) -> str:
        return "mean"
