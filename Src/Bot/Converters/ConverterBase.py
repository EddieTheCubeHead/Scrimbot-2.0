__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Generic, TypeVar

from discord.ext.commands import Context, Converter

from Bot.DataClasses.DataClass import DataClass
from Database.DatabaseConnections.ConnectionBase import ConnectionBase

T = TypeVar('T', bound=DataClass)  # pylint: disable=invalid-name


class ConverterBase(Generic[T], Converter):

    def __init__(self, connection: ConnectionBase):  # pragma: no cover
        self.connection: ConnectionBase[T] = connection

    async def convert(self, ctx: Context, argument: str) -> T:  # pragma: no cover
        pass
