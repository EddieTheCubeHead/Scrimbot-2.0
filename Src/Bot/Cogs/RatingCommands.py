__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.Checks.PermissionsCheck import PermissionsCheck
from Bot.Converters.GuildConverter import GuildConverter
from Bot.Converters.RatingConverter import RatingConverter
from Bot.Converters.UserRatingConverter import UserRatingConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.Game import Game
from Bot.DataClasses.GuildMember import PermissionLevel
from Bot.DataClasses.User import User
from Bot.EmbedSystem.RatingEmbedBuilder import RatingEmbedBuilder


class RatingCommands(commands.Cog):

    @BotDependencyInjector.inject
    def __init__(self, rating_converter: UserRatingConverter, guild_converter: GuildConverter,
                 embed_builder: RatingEmbedBuilder):
        self._rating_converter = rating_converter
        self._guild_converter = guild_converter
        self._embed_builder = embed_builder

    @commands.command()
    @commands.guild_only()
    @PermissionsCheck(PermissionLevel.admin)
    async def rating(self, ctx: ScrimContext, user: User, game: Game, rating: RatingConverter):
        """
        A command that sets the given user's rating for the given game as the given value. Only usable by admins

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        :param user: The user whose rating is being set
        :type user: User
        :param game: The game of which rating is being set for the given user
        :type game: Game
        :param rating: The rating value the user's rating for the game will be set as
        :type rating: RatingConverter
        """
        guild = self._guild_converter.get_guild(ctx.guild.id)
        new_rating = self._rating_converter.create_user_rating(rating, user, game, guild)
        await self._embed_builder.send(ctx, displayable=new_rating)

    @commands.command(aliases=["stats"])
    @commands.guild_only()
    async def statistics(self, ctx: ScrimContext, user: User, game: Game):
        """
        A command that displays given user's statistics for the given game

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        :param user: The user whose statistics are being requested
        :type user: User
        :param game: The game of which statistics for the given user are being requested
        :type game: Game
        """
        guild = self._guild_converter.get_guild(ctx.guild.id)
        new_rating = self._rating_converter.get_user_statistics(user, game, guild)
        await self._embed_builder.send(ctx, displayable=new_rating)


def setup(client: ScrimBotClient):
    client.add_cog(RatingCommands())
    print(f"Using cog {__name__}, with version {__version__}")
