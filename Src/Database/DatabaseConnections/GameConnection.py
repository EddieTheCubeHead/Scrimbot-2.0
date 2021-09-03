__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.Game import Game
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyConstructor.connection
class GameConnection(ConnectionBase[Game]):

    def get_game(self, search: str):
        with self._master_connection.get_session() as session:
            query = session.query(Game).join(Alias).filter((Game.name == search) | (Alias.name == search))
            game = query.one()
        return game

    def add(self, game: Game):
        with self._master_connection.get_session() as session:
            session.add(game)
