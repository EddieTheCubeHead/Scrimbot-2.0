__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.UserRating import UserRating
from Bot.DataClasses.UserScrimResult import UserScrimResult, Result
from Database.DatabaseConnections.UserScrimResultConnection import UserScrimResultConnection


@BotDependencyInjector.singleton
class UserScrimResultConverter(ConverterBase[UserScrimResult]):

    connection: UserScrimResultConnection

    @BotDependencyInjector.inject
    def __init__(self, connection: UserScrimResultConnection):
        super().__init__(connection)

    def create_result(self, user_rating: UserRating, scrim: Scrim, result: Result) -> UserScrimResult:
        return self.connection.create_result(user_rating, scrim, result)
