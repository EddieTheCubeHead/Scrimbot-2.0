__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException


class BotMissingScrimException(BotBaseUserException, commands.CheckFailure):
    """An exception that should be raised when a scrim cannot be found during checks."""

    def __init__(self, context: commands.Context, *, send_help=True):
        self._context = context
        self.send_help = send_help

    def get_description(self) -> str:
        return f"Seems like the channel '{self._context.channel.name}' is not registered for scrim usage."

    def _construct_help_portion(self, ctx: commands.Context) -> str:
        """An override from the parent class

        args
        ----

        :param ctx: The context of the command that caused the error
        :type ctx: commands.Context
        :return: A string that tells user which help commands can be used to get more info about the error
        :rtype: str
        """

        return f"To get help with registering channels, use the command '{ctx.prefix}help register'"