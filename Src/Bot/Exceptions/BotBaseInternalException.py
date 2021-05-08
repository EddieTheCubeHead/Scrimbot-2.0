__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands


class BotBaseInternalException(commands.CommandError):
    """A base class for all the exceptions excepted in the code that should get handled silently internally."""

    def __init__(self, message: str, *, log=True):
        """The constructor of the exception

        args
        ----

        :param message: The error message logged internally
        :type message: str

        kwargs
        ------

        :param log: Whether to log the exception, default True
        :type log: bool
        """

        self.log = log
        self._message = message

    def __str__(self) -> str:
        return self.get_message()

    def get_message(self) -> str:
        """A method to get the error message related to this error.

        args
        ----

        :return: The error message
        :rtype: str
        """

        return self._message
