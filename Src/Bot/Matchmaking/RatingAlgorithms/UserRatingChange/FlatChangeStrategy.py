__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import Result

from Src.Bot.Matchmaking.RatingAlgorithms.UserRatingChange.UserRatingChangeStrategy import UserRatingChangeStrategy


@HinteDI.singleton_implementation(base=UserRatingChangeStrategy, key='flat')
class FlatChangeStrategy(UserRatingChangeStrategy):

    def get_rating_change(self, user_rating: UserRating, result: Result, own_team_rating: int,
                          *opposing_team_ratings: int) -> int:
        if result == Result.LOSS:
            return -25
        elif result == Result.WIN:
            return 25
        return 0
