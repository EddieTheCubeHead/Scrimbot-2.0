__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.Checks.ActiveScrimCheck import ActiveScrimCheck
from Bot.Checks.FreeScrimCheck import FreeScrimCheck
from Bot.Cogs.Helpers.BotSettingsService import BotSettingsService
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.Core import checks
from Bot.Core import converters
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.Game import Game
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Bot.Converters.GameConverter import GameConverter
from Bot.Converters.VoiceChannelConverter import VoiceChannelConverter
from Bot.Logic.ScrimManager import ScrimManager
from Configs.Config import Config


async def _add_team_reactions(scrim: ScrimManager):
    for team in range(1, len(scrim.teams_manager.get_game_teams()) + 1):
        await scrim.message.add_reaction(emoji=f"{team}\u20E3")


class ScrimCommands(commands.Cog):
    """A cog housing the commands directly related to creating and manipulating scrims"""

    @BotDependencyInjector.inject
    def __init__(self, scrim_channel_converter: ScrimChannelConverter, response_builder: ScrimEmbedBuilder,
                 settings_service: BotSettingsService, scrims_manager: ActiveScrimsManager):
        self._scrim_channel_converter = scrim_channel_converter
        self._response_builder = response_builder
        self._settings_service = settings_service
        self._scrims_manager = scrims_manager

    @commands.command(aliases=['s'])
    @commands.guild_only()
    @FreeScrimCheck.decorate()
    async def scrim(self, ctx: ScrimContext, game: Game, deletion_time: int = 0):
        """A command that creates a scrim of the specified game on the channel

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        :param game: The game that should be used for creating the scrim
        :type game: Game
        :param deletion_time: The time in minutes that the scrim can be inactive before automatic deletion
        :type deletion_time: Optional[int]
        """

        scrim_channel = self._scrim_channel_converter.get_from_id(ctx.channel.id)
        scrim = self._scrims_manager.create_scrim(scrim_channel, game)
        message = await self._response_builder.send(ctx, displayable=scrim)
        await message.add_reaction(emoji="\U0001F3AE")  # video game controller
        await message.add_reaction(emoji="\U0001F441")  # eye
        scrim.message = message

    @commands.command(aliases=["l", "lockteams"])
    @commands.guild_only()
    @ActiveScrimCheck.decorate()
    async def lock(self, ctx: ScrimContext):
        """A command that locks a scrim when it has the required amount of players

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        """

        scrim = ctx.scrim
        scrim.lock()
        await ctx.message.delete()
        await self._response_builder.edit(scrim.message, displayable=scrim)
        await scrim.message.clear_reactions()
        await _add_team_reactions(scrim)

    @commands.group(aliases=["t", "maketeams"])
    @commands.guild_only()
    @checks.active_scrim()
    async def teams(self, ctx: ScrimContext):
        """A command group for creating teams

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        """

        if not ctx.invoked_subcommand:
            raise commands.CommandError(f"Invalid subcommand for command '{ctx.prefix}teams'.")

    @teams.command(aliases=["rand", "r", "shuffle", "s"])
    async def random(self, ctx: commands.Context):
        """A command in the teams group for creating random teams

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        """

    @commands.command(aliases=["begin"])
    @commands.guild_only()
    @ActiveScrimCheck.decorate()
    async def start(self, ctx: ScrimContext, move_voice: bool = True):
        """A command for starting a scrim with two full teams

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        :param move_voice: Whether the bot should automatically move the participants to voice channels, default True
        :type move_voice: bool
        """

        await ctx.message.delete()
        if move_voice:
            await ctx.scrim.teams_manager.try_move_to_voice()
        ctx.scrim.start()
        ctx.scrim.message.reactions.clear()
        await self._response_builder.edit(ctx.scrim.message, displayable=ctx.scrim)

    @commands.command(aliases=["win", "w", "victor", "v"])
    @commands.guild_only()
    @checks.active_scrim()
    async def winner(self, ctx: ScrimContext, winner: converters.parse_winner):
        """A command for finishing a scrim and declaring a winner

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        :param winner: The team that won the scrim, should be '1', '2' or 'tie' (some aliases exist though)
        :type winner: str
        """

        scrim = await ctx.scrim
        await scrim.finish(winner)
        await ctx.message.delete()

    @commands.command(aliases=["draw"])
    @commands.guild_only()
    @checks.active_scrim()
    async def tie(self, ctx: ScrimContext):
        """A command for finishing a scrim as a tie. Just calls the 'winner' command with 'tie' as argument

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        """

        await self.winner(ctx, "tie")

    @commands.command()
    @commands.guild_only()
    @checks.active_scrim()
    async def terminate(self, ctx: ScrimContext):
        """A command that forcefully terminates a scrim on the channel

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        """

        scrim = ctx.scrim
        await scrim.terminate(f"Scrim terminated manually by {ctx.author.display_name}")
        await ctx.message.delete()


def setup(client: ScrimBotClient):
    """A method for adding the cog to the bot

    args
    ----

    :param client: The instance of the bot the cog should be added into
    :type client: ScrimBotClient
    """

    client.add_cog(ScrimCommands())
    print(f"Using cog {__name__}, with version {__version__}")
