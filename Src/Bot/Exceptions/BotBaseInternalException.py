__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.Exceptions.BotBaseException import BotBaseException


class BotBaseInternalException(BotBaseException):
    """A base class for all the exceptions excepted in the code that should get handled silently internally."""

    def __init__(self, message: str, *, log=True):
        self.log = log
        self._message = message

    def __str__(self) -> str:
        return self.get_message()

    def get_message(self) -> str:
        return self._message
