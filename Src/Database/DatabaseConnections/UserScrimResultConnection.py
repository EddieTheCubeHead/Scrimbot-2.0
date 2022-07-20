__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.UserScrimResult import UserScrimResult, Result
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
class UserScrimResultConnection(ConnectionBase[UserScrimResult]):

    def create_result(self, user_id: int, rating_id: int, scrim_id: int, frozen_rating: int, result: Result) -> \
            UserScrimResult:
        new_result = UserScrimResult(user_id, rating_id, scrim_id, frozen_rating, result)
        with self._master_connection.get_session() as session:
            session.add(new_result)
        return new_result
