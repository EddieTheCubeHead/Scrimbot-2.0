__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.ConvertableConstructor import ConvertableConstructor


@ConvertableConstructor.converter
class ScrimConverter(ConverterBase):

    def convert(self, argument: str):
        pass
