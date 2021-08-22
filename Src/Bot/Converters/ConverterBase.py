__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from Database.DatabaseConnections.ConnectionBase import ConnectionBase


class ConverterBase(ABC):

    def __init__(self, connection: ConnectionBase):  # pragma: no cover
        self.connection: ConnectionBase = connection

    @abstractmethod
    async def convert(self, argument: str):  # pragma: no cover
        pass
