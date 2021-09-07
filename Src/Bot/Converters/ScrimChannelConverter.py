__version__ = "0.1"
__author__ = "Eetu Asikainen"

from functools import lru_cache

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


@BotDependencyInjector.singleton
class ScrimChannelConverter(ConverterBase[ScrimChannel]):

    connection: ScrimChannelConnection = None

    @BotDependencyInjector.inject
    def __init__(self, connection: ScrimChannelConnection):
        super().__init__(connection)

    @lru_cache
    def convert(self, argument: str) -> ScrimChannel:
        return self.connection.get_channel(int(argument))
