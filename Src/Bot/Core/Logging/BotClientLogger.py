__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.Core.Logging.LoggerBase import LoggerBase
from Configs.Config import Config


@HinteDI.singleton
class BotClientLogger(LoggerBase):

    @HinteDI.inject
    def __init__(self, config: Config):
        super().__init__("scrimbot client", config)
