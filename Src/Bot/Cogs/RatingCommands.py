__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.Converters.RatingConverter import RatingConverter
from Bot.Converters.UserRatingConverter import UserRatingConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.Game import Game
from Bot.DataClasses.User import User


class RatingCommands(commands.Cog):

    @BotDependencyInjector.inject
    def __init__(self, rating_converter: UserRatingConverter):
        self._rating_converter = rating_converter

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def rating(self, ctx: ScrimContext, user: User, game: Game, rating: RatingConverter):
        new_rating = self._rating_converter.set_user_rating(rating, user, game, ctx.guild)


def setup(client: ScrimBotClient):
    client.add_cog(RatingCommands())
    print(f"Using cog {__name__}, with version {__version__}")
