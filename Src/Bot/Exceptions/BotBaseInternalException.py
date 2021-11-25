__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotLogger import ScrimBotLogger
from Bot.Exceptions.BotBaseException import BotBaseException


class BotBaseInternalException(BotBaseException):
    """A base class for all the exceptions excepted in the code that should get handled silently internally."""

    @BotDependencyInjector.inject
    def __init__(self, message: str, logger: ScrimBotLogger, *, log=True):
        self.log = log
        self.logger = logger
        self._message = message

    def resolve(self, ctx: Context):
        if self.log:
            self.logger.warning(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' caused an "
                                f"unspecified exception with the following message: '{self._message}'")
