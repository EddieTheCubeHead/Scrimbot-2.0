__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from hintedi import HinteDI

from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import Result


@HinteDI.abstract_base
class UserRatingChangeStrategy(ABC):

    @abstractmethod
    def get_rating_change(self, user_rating: UserRating, result: Result, own_team_rating: int,
                          *opposing_team_ratings: int) -> int:
        pass
