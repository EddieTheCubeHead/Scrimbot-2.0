__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Generic, TypeVar

from Bot.DataClasses.DataClass import DataClass
from Database.DatabaseConnections.ConnectionBase import ConnectionBase

T = TypeVar('T', bound=DataClass)  # pylint: disable=invalid-name


class ConverterBase(Generic[T]):

    def __init__(self, connection: ConnectionBase):  # pragma: no cover
        self.connection: ConnectionBase[T] = connection

    def convert(self, argument: str) -> T:  # pragma: no cover
        pass
