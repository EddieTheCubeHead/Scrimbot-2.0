__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

class BotBaseInternalException(commands.CommandError):
    """A base class for all the exceptions excepted in the code that should get handled silently internally."""

    def __init__(self, message: str):
        """The constructor of the exception

        :param message: The error message logged internally
        :type message: str
        """

        self.message = message
