__version__ = "ver"
__author__ = "Eetu Asikainen"

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector


@BotDependencyInjector.singleton
class ${NAME}(ConverterBase[DataClass]):
    pass

    
