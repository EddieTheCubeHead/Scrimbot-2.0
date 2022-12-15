__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

from hintedi import HinteDI

from Src.Bot.Converters.ConverterBase import ConverterBase
from Src.Bot.Converters.UserScrimResultConverter import UserScrimResultConverter
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Guild import Guild
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.User import User
from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import Result
from Database.DatabaseConnections.UserRatingConnection import UserRatingConnection


@HinteDI.singleton
class UserRatingConverter(ConverterBase):

    connection: UserRatingConnection

    @HinteDI.inject
    def __init__(self, connection: UserRatingConnection, result_converter: UserScrimResultConverter):
        super().__init__(connection)
        self._result_converter = result_converter

    def get_user_rating(self, user: User, game: Game, guild: Optional[Guild]) -> UserRating:
        return self.connection.get_user_rating(user, game, guild)

    def get_user_statistics(self, user: User, game: Game, guild: Optional[Guild]) -> UserRating:
        rating = self.connection.get_user_statistics(user, game, guild)
        rating.user.member = user.member
        return rating

    def set_user_rating(self, rating: int, user: User, game: Game, guild: Optional[Guild]) -> UserRating:
        return self.connection.set_user_rating(rating, user, game, guild)

    def create_user_rating(self, rating: int, user: User, game: Game, guild: Optional[Guild]) -> UserRating:
        self.connection.set_user_rating(rating, user, game, guild)
        return self.get_user_statistics(user, game, guild)

    def update_user_rating(self, change: int, result: Result, user: User, scrim: Scrim, guild: Optional[Guild])\
            -> UserRating:
        original_rating = self.connection.get_user_rating(user, scrim.game, guild)
        self._result_converter.create_result(original_rating, scrim, result)
        return self.connection.set_user_rating(original_rating.rating + change, user, scrim.game, guild)
