__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder, T


@BotDependencyInjector.instance
class RatingEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, displayable: T) -> Embed:
        pass
