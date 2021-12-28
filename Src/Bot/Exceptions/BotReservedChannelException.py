__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import TextChannel

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


def _construct_message(reserved_channel_id: int, parent_channel_id: int):
    if parent_channel_id is None:
        return f"Text channel <#{reserved_channel_id}> is already registered for scrim usage."
    return f"Voice channel <#{reserved_channel_id}> is already associated with scrim channel <#{parent_channel_id}>."


class BotReservedChannelException(BotBaseRespondToContextException):

    @BotDependencyInjector.inject
    def __init__(self, reserved_channel_id: int, embed_builder: ExceptionEmbedBuilder, parent_channel_id: int = None):
        self.message = _construct_message(reserved_channel_id, parent_channel_id)
        super().__init__(self.message, embed_builder)
