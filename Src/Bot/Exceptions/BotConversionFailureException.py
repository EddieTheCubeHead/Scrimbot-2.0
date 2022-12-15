__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from hintedi import HinteDI

from Src.Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


def _build_message(conversion_type: str, argument: str) -> str:
    return f"Could not convert argument '{argument}' into type {conversion_type}"


class BotConversionFailureException(BotBaseRespondToContextException, commands.ConversionError):

    @HinteDI.inject
    def __init__(self, conversion_type: str, argument: str, embed_builder: ExceptionEmbedBuilder, reason=None):
        message = _build_message(conversion_type, argument)
        if reason is not None:
            message += f" because {reason}"
        super().__init__(message, embed_builder)
