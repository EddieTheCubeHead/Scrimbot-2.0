__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import CheckFailure

from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotChannelHasScrimException(BotBaseRespondToContextException, CheckFailure):

    def __init__(self, channel_id: int):
        message = f"Cannot create a scrim on channel <#{channel_id}> because the channel already has an active scrim."
        super().__init__(message)