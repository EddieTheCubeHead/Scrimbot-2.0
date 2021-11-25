__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import CommandNotFound, Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Bot.Exceptions.BotBaseUserException import BotBaseUserException


class BotUnrecognizedCommandException(BotBaseUserException):

    @BotDependencyInjector.inject
    def __init__(self, context: Context, embed_builder: ExceptionEmbedBuilder):
        message = f"Could not recognize command '{context.invoked_with}'"
        super().__init__(message, embed_builder)
