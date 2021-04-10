__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException

class BotCheckFailure(BotBaseUserException, commands.CheckFailure):
    """An exception that should get raised when the bot fails a check."""

    def get_header(self) -> str:
        return "Check failed:"