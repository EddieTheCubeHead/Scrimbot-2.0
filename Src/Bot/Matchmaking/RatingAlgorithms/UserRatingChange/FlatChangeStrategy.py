__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.UserRating import UserRating
from Bot.DataClasses.UserScrimResult import Result

from Bot.Matchmaking.RatingAlgorithms.UserRatingChange.UserRatingChangeStrategy import UserRatingChangeStrategy


class FlatChangeStrategy(UserRatingChangeStrategy):

    def get_rating_change(self, user_rating: UserRating, result: Result, own_team_rating: int,
                          *opposing_team_ratings: int) -> int:
        if result == Result.LOSS:
            return -25
        elif result == Result.WIN:
            return 25
        return 0
