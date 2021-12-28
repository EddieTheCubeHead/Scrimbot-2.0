__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotCheckFailure(BotBaseRespondToContextException, commands.CheckFailure):
    """An exception that should get raised when the bot fails a check."""

    def get_header(self) -> str:
        return "Check failed:"
