__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.ScrimClient import ScrimClient
import Src.Bot.checks as checks
import Src.Bot.converters as converters
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException

class ScrimCommands(commands.Cog):
    """A cog housing the commands directly related to creating and manipulating scrims

    Commands
    --------
    scrim(ctx, game, deletion_time = 0)
        Creates a scrim of the specified game, that will be deleted after the given amount of time
    """

    def __init__(self, client: ScrimClient):
        """The constructor of the ScrimCommands cog.

        args
        ----

        :param client: The client instance associated with this cog.
        :type client: ScrimClient
        """

        self._client = client

    @commands.command(aliases=['s'])
    @commands.guild_only()
    @checks.free_scrim()
    async def scrim(self, ctx: commands.Context, game: Game, deletion_time: int = 0):
        """A command that creates a scrim of the specified game on the channel

        args
        ----

        :param ctx: The invokation context of the command
        :type ctx: commands.Context
        :param game: The game that should be used for creating the scrim
        :type game: Game
        :param deletion_time: The time in minutes that the scrim can be inactive before automatic deletion
        :type deletion_time: Optional[int]
        """

        deletion_time = deletion_time or await self._client.get_deletion_time(ctx)
        await ctx.scrim.create(ctx, game, deletion_time)
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @checks.active_scrim()
    async def lock(self, ctx: commands.Context):
        """A command that locks a scrim when it has the required amount of players

        args
        ----

        :param ctx: The invokation context of the command
        :type ctx: commands.Context
        """

        await ctx.scrim.lock()
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @checks.active_scrim()
    async def teams(self, ctx: commands.Context):
        """A command group for creating teams

        args
        ----

        :param ctx: The invokation context of the command
        :type ctx: commands.Context
        """

        if not ctx.invoked_subcommand:
            raise commands.CommandError(f"Invalid subcommand for command '{ctx.prefix}teams'.")

    @commands.command()
    @commands.guild_only()
    @checks.active_scrim()
    async def start(self, ctx: commands.Context, move_voice: bool = True):
        """A command for starting a scrim with two full teams

        args
        ----

        :param ctx: The invokation context of the command
        :type ctx: commands.Context
        :param move_voice: Whether the bot should automatically move the participants to voice channels, default True
        :type move_voice: bool
        """

        await ctx.scrim.start(ctx, move_voice)
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @checks.active_scrim()
    async def winner(self, ctx: commands.Context, winner: converters.parse_winner):
        """A command for finishing a scrim and declaring a winner

        args
        ----

        :param ctx: The invokation context of the command
        :type ctx: commands.Context
        :param winner: The team that won the scrim, should be '1', '2' or 'tie' (some aliases exist though)
        :type winner: str
        """

        # await ctx.scrim.finish(winner)
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @checks.active_scrim()
    async def terminate(self, ctx: commands.Context):
        """A command that forcefully terminates a scrim on the channel

        args
        ----

        :param ctx: The invokation context of the command
        :type ctx: commands.Context
        """

        await ctx.scrim.terminate(f"Scrim terminated manually by {ctx.author.display_name}")
        await ctx.message.delete()


def setup(client: commands.Bot):
    """A method for adding the cog to the bot

    args
    ----

    :param client: The instance of the bot the cog should be added into
    :type client: ScrimClient
    """

    client.add_cog(ScrimCommands(client))
    print(f"Using cog {__name__}, with version {__version__}")
