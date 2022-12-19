__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.Core.Logging.LoggerBase import LoggerBase
from Src.Configs.Config import Config


@HinteDI.singleton
class BotSystemLogger(LoggerBase):

    @HinteDI.inject
    def __init__(self, config: Config):
        super().__init__("scrimbot system", config)
