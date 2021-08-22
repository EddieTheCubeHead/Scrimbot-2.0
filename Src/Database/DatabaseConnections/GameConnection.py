__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.Game import Game
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


class GameConnection(ConnectionBase[Game]):

    def get_from_id(self, object_id: int) -> Game:
        pass

    def get_multiple(self, *object_ids: int) -> list[Game]:
        pass

    def get_all(self) -> list[Game]:
        pass

    def insert(self, new_object: Game):
        pass

    def update(self, updated_object: Game):
        pass
