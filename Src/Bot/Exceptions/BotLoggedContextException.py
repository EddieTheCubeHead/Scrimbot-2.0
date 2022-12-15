__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import WARNING, DEBUG, INFO, ERROR, CRITICAL

from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.Core.Logging.BotClientLogger import BotClientLogger
from Src.Bot.Exceptions.BotBaseContextException import BotBaseContextException


def log_with_level(log, logger, message):
    if log == DEBUG:
        logger.debug(message)
    if log == INFO:
        logger.info(message)
    if log == WARNING:
        logger.warning(message)
    if log == ERROR:
        logger.error(message)
    if log == CRITICAL:
        logger.critical(message)


class BotLoggedContextException(BotBaseContextException):
    """A base class for all the exceptions excepted in the code that should get handled silently internally."""

    @HinteDI.inject
    def __init__(self, message: str, logger: BotClientLogger, *, log: int = WARNING):
        self.log = log
        self.logger = logger
        self.message = message

    def resolve(self, ctx: Context):
        message = f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' caused an unspecified " \
                  f"exception with the following message: '{self.message}'"
        log_with_level(self.log, self.logger, message)
