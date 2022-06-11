__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from typing_extensions import Annotated

from Bot.Checks.ActiveScrimCheck import ActiveScrimCheck
from Bot.Checks.FreeScrimCheck import FreeScrimCheck
from Bot.Cogs.Helpers.BotSettingsService import BotSettingsService
from Bot.Cogs.Helpers.WaitingScrimService import WaitingScrimService
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.Converters.ScrimResultConverter import ScrimResultConverter, ScrimResult
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.Game import Game
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Bot.Converters.GameConverter import GameConverter
from Bot.Converters.VoiceChannelConverter import VoiceChannelConverter
from Bot.Logic.ScrimManager import ScrimManager
from Bot.Matchmaking.TeamCreationStrategy import TeamCreationStrategy
from Bot.Matchmaking.RandomTeamsStrategy import RandomTeamsStrategy
from Bot.Matchmaking.ClearTeamsStrategy import ClearTeamsStrategy
from Configs.Config import Config


async def _add_team_reactions(scrim: ScrimManager):
    for team in range(1, len(scrim.teams_manager.get_game_teams()) + 1):
        await scrim.message.add_reaction(emoji=f"{team}\u20E3")


class ScrimCommands(commands.Cog):
    """A cog housing the commands directly related to creating and manipulating scrims"""

    @BotDependencyInjector.inject
    def __init__(self, scrim_channel_converter: ScrimChannelConverter, response_builder: ScrimEmbedBuilder,
                 settings_service: BotSettingsService, scrims_manager: ActiveScrimsManager,
                 waiting_scrim_service: WaitingScrimService):
        self._scrim_channel_converter = scrim_channel_converter
        self._response_builder = response_builder
        self._settings_service = settings_service
        self._scrims_manager = scrims_manager
        self._waiting_scrim_service = waiting_scrim_service

    @commands.command(aliases=['s'])
    @commands.guild_only()
    @FreeScrimCheck()
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
    @ActiveScrimCheck()
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

    @commands.command(aliases=["t", "maketeams"])
    @commands.guild_only()
    @ActiveScrimCheck()
    async def teams(self, ctx: ScrimContext, criteria: TeamCreationStrategy):
        """A command group for creating teams

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        :param criteria: The criteria used for creating the teams
        :type criteria: TeamCreationStrategy
        """

        scrim = ctx.scrim
        await criteria.create_teams(scrim)
        await ctx.message.delete()
        await self._response_builder.edit(scrim.message, displayable=scrim)

    @commands.command(aliases=["begin"])
    @commands.guild_only()
    @ActiveScrimCheck()
    async def start(self, ctx: ScrimContext, move_voice: bool = True):
        """A command for starting a scrim with two full teams

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        :param move_voice: Whether the bot should automatically move the participants to voice channels, default True
        :type move_voice: bool
        """

        await ctx.message.delete()
        started = True
        if move_voice and ctx.scrim.teams_manager.supports_voice:
            started = await ctx.scrim.start_with_voice()
        else:
            ctx.scrim.start()
        if started:
            await ctx.scrim.message.clear_reactions()
        else:
            self._waiting_scrim_service.register(ctx.scrim)
        await self._response_builder.edit(ctx.scrim.message, displayable=ctx.scrim)

    @commands.command(aliases=["win", "w", "victor", "v"])
    @commands.guild_only()
    @ActiveScrimCheck()
    async def winner(self, ctx: ScrimContext, winner: ScrimResultConverter):
        """A command for finishing a scrim and declaring a winner

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        :param winner: The team that won the scrim, should be a number or team name
        :type winner: str
        """

        scrim = ctx.scrim
        await scrim.end(winner)
        await ctx.message.delete()
        await self._response_builder.edit(ctx.scrim.message, displayable=ctx.scrim)

    @commands.command(aliases=["draw"])
    @commands.guild_only()
    @ActiveScrimCheck()
    async def tie(self, ctx: ScrimContext):
        """A command for finishing a scrim as a tie. Just calls the 'winner' command with 'tie' as argument

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        """

        await self.winner(ctx, [tuple(team for team in ctx.scrim.teams_manager.get_game_teams())])

    @commands.command()
    @commands.guild_only()
    @ActiveScrimCheck()
    async def end(self, ctx: ScrimContext):
        """A command for finishing a scrim without registering the results

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        """

        await self.winner(ctx, [])

    @commands.command()
    @commands.guild_only()
    @ActiveScrimCheck()
    async def terminate(self, ctx: ScrimContext):
        """A command that forcefully terminates a scrim on the channel

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: ScrimContext
        """

        scrim = ctx.scrim
        scrim.terminate(ctx.author)
        await ctx.message.delete()
        await self._response_builder.edit(ctx.scrim.message, displayable=ctx.scrim)
        await scrim.message.clear_reactions()
        self._scrims_manager.drop(scrim)


def setup(client: ScrimBotClient):
    client.add_cog(ScrimCommands())
    print(f"Using cog {__name__}, with version {__version__}")
