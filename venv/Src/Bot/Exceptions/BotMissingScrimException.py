__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException

class BotMissingScrimException(BotBaseUserException, commands.CheckFailure):
    """An exception that should be raised when a scrim cannot be found during checks."""

    def __init__(self, context: commands.Context, channel: discord.TextChannel):
        self._context = context

    def get_description(self) -> str:
        return f"Seems like the channel '{self._context.channel.name}' is not registered for scrim usage."