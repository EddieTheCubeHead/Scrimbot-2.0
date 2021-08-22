__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from Bot.Converters.Convertable import Convertable
from Database.DatabaseConnections.ConnectionBase import ConnectionBase

T = TypeVar('T', bound=Convertable)


class ConverterBase(Generic[T]):

    def __init__(self, connection: ConnectionBase):  # pragma: no cover
        self.connection: ConnectionBase[T] = connection

    async def convert(self, argument: str) -> T:  # pragma: no cover
        pass
