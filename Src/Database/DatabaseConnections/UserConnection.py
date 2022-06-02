__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.User import User
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
class UserConnection(ConnectionBase[User]):

    def get_user(self, user_id: int):
        with self._master_connection.get_session() as session:
            query = session.query(User).filter(User.user_id == user_id)
            user = query.first()
        return user or self._create_user(user_id)

    def _create_user(self, user_id: int):
        from Bot.DataClasses.User import User
        new_user = User(user_id)
        with self._master_connection.get_session() as session:
            session.add(new_user)
        return new_user
