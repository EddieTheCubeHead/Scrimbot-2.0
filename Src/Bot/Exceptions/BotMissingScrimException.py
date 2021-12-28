__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotMissingScrimException(BotBaseRespondToContextException, commands.CheckFailure):
    """An exception that should be raised when a scrim cannot be found during checks."""

    def __init__(self, context: commands.Context, *, send_help=True):
        self._context = context
        self.send_help = send_help
        self.message = f"Seems like the channel '{context.channel.name}' is not registered for scrim usage."
