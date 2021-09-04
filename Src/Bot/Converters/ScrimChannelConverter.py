__version__ = "0.1"
__author__ = "Eetu Asikainen"

from functools import lru_cache

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


@BotDependencyConstructor.converter
class ScrimChannelConverter(ConverterBase[ScrimChannel]):  # pylint: disable=too-few-public-methods

    connection: ScrimChannelConnection = None

    @lru_cache
    def convert(self, argument: str) -> ScrimChannel:
        return self.connection.get_channel(int(argument))
