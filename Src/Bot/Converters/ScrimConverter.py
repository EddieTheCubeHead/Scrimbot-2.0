__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.ConvertableConstructor import ConvertableConstructor
from Bot.DataClasses.Scrim import Scrim


@ConvertableConstructor.converter
class ScrimConverter(ConverterBase[Scrim]):

    def convert(self, argument: str) -> Scrim:
        pass
