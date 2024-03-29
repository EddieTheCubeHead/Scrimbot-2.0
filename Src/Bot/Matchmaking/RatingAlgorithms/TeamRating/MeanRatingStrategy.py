__version__ = "0.1"
__author__ = "Eetu Asikainen"

from statistics import mean

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.UserRating import UserRating
from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategy import TeamRatingStrategy


@BotDependencyInjector.singleton
class MeanRatingStrategy(TeamRatingStrategy):

    def get_rating(self, *member_ratings: UserRating) -> float:
        return mean([member_rating.rating for member_rating in member_ratings])

    @property
    def name(self) -> str:
        return "mean"
