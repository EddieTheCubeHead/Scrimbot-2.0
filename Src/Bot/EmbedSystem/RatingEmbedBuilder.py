__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.UserRating import UserRating
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


@BotDependencyInjector.instance
class RatingEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, rating: UserRating) -> Embed:
        embed = Embed(title="Player statistics", description=f"<@{rating.user_id}>")
        embed.set_author(name=rating.game_name)
        return embed
