__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

class BotBaseUserException(commands.CommandError):
    """A base class for all the exceptions caused by the user activity (input/actions) thrown by the bot."""

    def __init__(self, message: str, *, send_help=True):
        """The constructor of the exception.

        args
        ----

        :param message: The error message displayed to the user.
        :type message: str

        kwargs
        ------

        :param send_help: Whether the help command format should be sent as part of the exception handling, default True
        :type send_help: bool
        """

        self._message = message
        self.send_help = send_help

    def get_header(self) -> str:
        """A method that returns a text header for the error (eg. whether it's an error, check failure, etc.).

        args
        ----

        :return: A corresponding header
        :rtype: str
        """

        return "Error:"

    def get_description(self) -> str:
        """A method that returns a text description of the error.

        args
        ----

        :return: A string detailing the exception's occurrence reason
        :rtype: str
        """

        return self._message