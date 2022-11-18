__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import WARNING

from hintedi import HinteDI

from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.Exceptions.BotBaseNoContextException import BotBaseNoContextException
from Bot.Exceptions.BotLoggedContextException import log_with_level


class BotLoggedNoContextException(BotBaseNoContextException):

    @HinteDI.inject
    def __init__(self, message: str, logger: BotSystemLogger, *, log=WARNING):
        self.log = log
        self.logger = logger
        self.message = message

    def resolve(self):
        message = f"An exception occurred during bot operation: {self.message}"
        log_with_level(self.log, self.logger, message)
