__version__ = "0.1"
__author__ = "Eetu Asikainen"

from math import sqrt

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.UserRating import UserRating
from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategy import TeamRatingStrategy


@BotDependencyInjector.singleton
class WeightBestPlayerRatingStrategy(TeamRatingStrategy):

    def get_rating(self, *member_ratings: UserRating) -> float:
        ratings = [member.rating for member in member_ratings]
        return (sum(ratings) + sqrt((sum(ratings) / len(ratings)) * max(ratings))) / (len(ratings) + 1)

    @property
    def name(self) -> str:
        return "weighted_best"
