__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import UserScrimResult, Result
from Src.Database.DatabaseConnections.ConnectionBase import ConnectionBase


@HinteDI.singleton
class UserScrimResultConnection(ConnectionBase[UserScrimResult]):

    def create_result(self, user_rating: UserRating, scrim: Scrim, result: Result) -> \
            UserScrimResult:
        new_result = UserScrimResult(user_rating.user_id, user_rating.rating_id, scrim.scrim_id, user_rating.rating,
                                     result)
        with self._master_connection.get_session() as session:
            session.add(new_result)
        return new_result
