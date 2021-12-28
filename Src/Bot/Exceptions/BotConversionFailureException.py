__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


def _build_message(conversion_type: str, argument: str) -> str:
    return f"Could not convert argument '{argument}' into type {conversion_type}"


class BotConversionFailureException(BotBaseRespondToContextException, commands.ConversionError):

    @BotDependencyInjector.inject
    def __init__(self, conversion_type: str, argument: str, embed_builder: ExceptionEmbedBuilder):
        message = _build_message(conversion_type, argument)
        super().__init__(message, embed_builder)
