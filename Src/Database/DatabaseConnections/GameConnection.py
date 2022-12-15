__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload, selectinload

from hintedi import HinteDI

from Src.Bot.DataClasses.Alias import Alias
from Src.Bot.DataClasses.Game import Game
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@HinteDI.singleton
class GameConnection(ConnectionBase[Game]):

    def get_game(self, search: str) -> Game:
        with self._master_connection.get_session() as session:
            query = session.query(Game).join(Alias).filter((Game.name == search) | (Alias.name == search))
            game = query.one()
        return game

    def add(self, game: Game):
        with self._master_connection.get_session() as session:
            session.add(game)

    def get_all(self) -> list[Game]:
        with self._master_connection.get_session() as session:
            query = session.query(Game).join(Alias).options(selectinload(Game.aliases))
            games = query.all()
        return games
