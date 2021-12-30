__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotMissingScrimException(BotBaseRespondToContextException, commands.CheckFailure):
    """An exception that should be raised when a scrim cannot be found during checks."""

    def __init__(self, channel_id: int):
        super().__init__(f"Could not find a scrim from channel <#{channel_id}>.")
