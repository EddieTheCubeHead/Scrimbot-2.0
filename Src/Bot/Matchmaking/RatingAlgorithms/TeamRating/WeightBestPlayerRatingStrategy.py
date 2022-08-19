__version__ = "0.1"
__author__ = "Eetu Asikainen"

from math import sqrt
from statistics import mean

from Bot.DataClasses.UserRating import UserRating
from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategy import TeamRatingStrategy


class WeightBestPlayerRatingStrategy(TeamRatingStrategy):

    def get_rating(self, *member_ratings: UserRating) -> float:
        ratings = [member.rating for member in member_ratings]
        return (sum(ratings) + sqrt((sum(ratings) / len(ratings)) * max(ratings))) / (len(ratings) + 1)
