__version__ = "ver"
__author__ = "Eetu Asikainen"

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor


@BotDependencyConstructor.converter
class ${NAME}(ConverterBase[Convertable]):
    pass

    
