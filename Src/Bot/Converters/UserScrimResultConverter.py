__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.Converters.ConverterBase import ConverterBase
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import UserScrimResult, Result
from Database.DatabaseConnections.UserScrimResultConnection import UserScrimResultConnection


@HinteDI.singleton
class UserScrimResultConverter(ConverterBase[UserScrimResult]):

    connection: UserScrimResultConnection

    @HinteDI.inject
    def __init__(self, connection: UserScrimResultConnection):
        super().__init__(connection)

    def create_result(self, user_rating: UserRating, scrim: Scrim, result: Result) -> UserScrimResult:
        return self.connection.create_result(user_rating, scrim, result)
