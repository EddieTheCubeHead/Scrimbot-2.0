__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotUnrecognizedCommandException(BotBaseRespondToContextException):

    @HinteDI.inject
    def __init__(self, context: Context, embed_builder: ExceptionEmbedBuilder):
        message = f"Could not recognize command '{context.invoked_with}'"
        super().__init__(message, embed_builder)
