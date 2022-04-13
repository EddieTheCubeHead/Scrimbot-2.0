__version__ = "ver"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Scrim import Scrim
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
class ScrimConnection(ConnectionBase):

    def add_scrim(self, scrim: Scrim) -> Scrim:
        with self._master_connection.get_session() as session:
            session.add(scrim)
        return scrim
