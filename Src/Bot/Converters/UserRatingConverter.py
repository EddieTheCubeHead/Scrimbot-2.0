__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.User import User
from Bot.DataClasses.UserRating import UserRating
from Database.DatabaseConnections.UserRatingConnection import UserRatingConnection


@BotDependencyInjector.singleton
class UserRatingConverter(ConverterBase):

    connection: UserRatingConnection

    @BotDependencyInjector.inject
    def __init__(self, connection: UserRatingConnection):
        super().__init__(connection)

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
