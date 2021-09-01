__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.DataClasses.ScrimChannel import ScrimChannel


@BotDependencyConstructor.converter
class ScrimChannelConverter(ConverterBase[ScrimChannel]):

    def convert(self, argument: str) -> ScrimChannel:
        pass
