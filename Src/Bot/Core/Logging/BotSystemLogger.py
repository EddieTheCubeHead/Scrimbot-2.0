__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.LoggerBase import LoggerBase
from Configs.Config import Config


@BotDependencyInjector.singleton
class BotSystemLogger(LoggerBase):

    @BotDependencyInjector.inject
    def __init__(self, config: Config):
        super().__init__("scrimbot system", config)
