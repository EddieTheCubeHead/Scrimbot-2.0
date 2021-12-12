__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import WARNING, DEBUG, INFO, ERROR, CRITICAL

from discord.ext import commands
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotLogger import ScrimBotLogger
from Bot.Exceptions.BotBaseException import BotBaseException


class BotBaseInternalException(BotBaseException):
    """A base class for all the exceptions excepted in the code that should get handled silently internally."""

    @BotDependencyInjector.inject
    def __init__(self, message: str, logger: ScrimBotLogger, *, log: int = WARNING):
        self.log = log
        self.logger = logger
        self.message = message

    def resolve(self, ctx: Context):
        message = f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' caused an unspecified " \
                  f"exception with the following message: '{self.message}'"
        if self.log == DEBUG:
            self.logger.debug(message)
        if self.log == INFO:
            self.logger.info(message)
        if self.log == WARNING:
            self.logger.warning(message)
        if self.log == ERROR:
            self.logger.error(message)
        if self.log == CRITICAL:
            self.logger.critical(message)
