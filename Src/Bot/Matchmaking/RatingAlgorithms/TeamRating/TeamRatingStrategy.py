__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from hintedi import HinteDI

from Bot.DataClasses.UserRating import UserRating


@HinteDI.abstract_base
class TeamRatingStrategy(ABC):

    @abstractmethod
    def get_rating(self, *member_ratings: UserRating) -> float:
        pass
