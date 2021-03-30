__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

class BotBaseUserException(commands.CommandError):
    """A base class for all the exceptions caused by the user thrown by the bot."""

    def __init__(self, message: str):
        """The constructor of the exception

        :param message: The error message displayed to the user.
        :type message: str
        """
        self.message = message