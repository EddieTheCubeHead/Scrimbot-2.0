__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import CheckFailure

from Bot.Exceptions.BotBaseUserException import BotBaseUserException


class BotUnregisteredChannelException(BotBaseUserException, CheckFailure):

    def __init__(self, channel_id: int):
        message = f"Cannot create a scrim on channel <#{channel_id}> because it is not registered for scrim " \
                       f"usage."
        super().__init__(message)
