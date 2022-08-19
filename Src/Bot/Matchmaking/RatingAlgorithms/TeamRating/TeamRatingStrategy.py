__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from Bot.DataClasses.UserRating import UserRating


class TeamRatingStrategy(ABC):

    @abstractmethod
    def get_rating(self, *member_ratings: UserRating) -> float:
        pass
