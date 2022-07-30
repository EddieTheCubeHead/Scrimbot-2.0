__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from Bot.DataClasses.UserRating import UserRating
from Bot.DataClasses.UserScrimResult import Result


class UserRatingChangeStrategy(ABC):

    @abstractmethod
    def get_rating_change(self, user_rating: UserRating, result: Result, own_team_rating: int,
                          *opposing_team_ratings: int) -> int:
        pass
