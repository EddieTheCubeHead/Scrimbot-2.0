__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException

class BotMissingScrimException(BotBaseUserException, commands.CheckFailure):
    """An exception that should be raised when a scrim cannot be found during checks."""

    def __init__(self, context: commands.Context, channel: discord.TextChannel, *, send_help=True):
        self._context = context
        self.send_help = send_help

    def get_description(self) -> str:
        return f"Seems like the channel '{self._context.channel.name}' is not registered for scrim usage."