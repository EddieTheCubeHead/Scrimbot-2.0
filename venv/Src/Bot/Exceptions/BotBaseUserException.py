__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

class BotBaseUserException(commands.CommandError):
    """A base class for all the exceptions caused by the user activity (input/actions) thrown by the bot."""

    def __init__(self, message: str):
        """The constructor of the exception.

        :param message: The error message displayed to the user.
        :type message: str
        """

        self._message = message

    def get_header(self) -> str:
        """A method that returns a text header for the error (eg. whether it's an error, check failure, etc.).

        :return: A corresponding header
        :rtype: str
        """

        return "Error:"

    def get_description(self) -> str:
        """A method that returns a text description of the error.

        :return: A string detailing the exception's occurrence reason
        :rtype: str
        """

        return self._message