__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.UserRating import UserRating
from Bot.DataClasses.UserScrimResult import UserScrimResult, Result
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
class UserScrimResultConnection(ConnectionBase[UserScrimResult]):

    def create_result(self, user_rating: UserRating, scrim: Scrim, result: Result) -> \
            UserScrimResult:
        new_result = UserScrimResult(user_rating.user_id, user_rating.rating_id, scrim.scrim_id, user_rating.rating,
                                     result)
        with self._master_connection.get_session() as session:
            session.add(new_result)
        return new_result
