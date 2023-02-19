__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Message
from discord.ext import commands
from hintedi import HinteDI

from Src.Bot.Checks.ActiveScrimCheck import ActiveScrimCheck
from Src.Bot.Checks.FreeScrimCheck import FreeScrimCheck
from Src.Bot.Cogs.Helpers.BotSettingsService import BotSettingsService
from Src.Bot.Cogs.Helpers.ScrimVoiceOperationService import ScrimVoiceOperationService
from Src.Bot.Cogs.Helpers.WaitingScrimService import WaitingScrimService
from Src.Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Src.Bot.Converters.ScrimConverter import ScrimConverter
from Src.Bot.Converters.ScrimResultConverter import ScrimResultConverter
from Src.Bot.Core.ScrimBotClient import ScrimBotClient
from Src.Bot.Core.ScrimContext import ScrimContext
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Scrim import ScrimState, Scrim
from Src.Bot.EmbedSystem.NewScrimEmbedBuilder import NewScrimEmbedBuilder
from Src.Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Src.Bot.Logic.ScrimManager import ScrimManager
from Src.Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Src.Bot.Matchmaking.ResultHandler import ResultHandler
from Src.Bot.Matchmaking.TeamCreation.TeamCreationStrategy import TeamCreationStrategy
# These need to be imported to enable registering them for DI
from Src.Bot.Converters.GameConverter import GameConverter
from Src.Bot.Converters.VoiceChannelConverter import VoiceChannelConverter
from Src.Bot.Matchmaking.TeamCreation.RandomTeamsStrategy import RandomTeamsStrategy
from Src.Bot.Matchmaking.TeamCreation.ClearTeamsStrategy import ClearTeamsStrategy
from Src.Configs.Config import Config
from Src.Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Src.Bot.EmbedSystem.ScrimStates.CaptainsPreparationState import CaptainsPreparationState
from Src.Bot.EmbedSystem.ScrimStates.CaptainsState import CaptainsState
from Src.Bot.EmbedSystem.ScrimStates.EndedState import EndedState
from Src.Bot.EmbedSystem.ScrimStates.LockedState import LockedState
from Src.Bot.EmbedSystem.ScrimStates.LookingForPlayersState import LookingForPlayersState
from Src.Bot.EmbedSystem.ScrimStates.SettingUpState import SettingUpState
from Src.Bot.EmbedSystem.ScrimStates.TerminatedState import TerminatedState
from Src.Bot.EmbedSystem.ScrimStates.WaitingForVoiceState import WaitingForVoiceState
from Src.Bot.Matchmaking.RatingAlgorithms.UserRatingChange.FlatChangeStrategy import FlatChangeStrategy
from Src.Bot.Matchmaking.RatingAlgorithms.TeamRating.MeanRatingStrategy import MeanRatingStrategy
from Src.Bot.Matchmaking.RatingAlgorithms.TeamRating.WeightBestPlayerRatingStrategy import WeightBestPlayerRatingStrategy


async def _add_team_reactions(scrim: Scrim, state: ScrimStateBase, message: Message):
    for team in range(1, len(state.get_game_teams(scrim)) + 1):
        await message.add_reaction(emoji=f"{team}\u20E3")


class ScrimCommands(commands.Cog):
    """A cog housing the commands directly related to creating and manipulating scrims"""

    @HinteDI.inject
    def __init__(self, scrim_channel_converter: ScrimChannelConverter, response_builder: NewScrimEmbedBuilder,
                 settings_service: BotSettingsService, scrim_converter: ScrimConverter,
                 scrims_manager: ActiveScrimsManager, waiting_scrim_service: WaitingScrimService,
                 participant_provider: ScrimParticipantProvider, result_handler: ResultHandler,
                 scrim_state_provider: ScrimStateBase, voice_operation_service: ScrimVoiceOperationService):
        self._scrim_channel_converter = scrim_channel_converter
        self._response_builder = response_builder
        self._settings_service = settings_service
        self._scrim_converter = scrim_converter
        self._scrims_manager = scrims_manager
        self._waiting_scrim_service = waiting_scrim_service
        self._participant_provider = participant_provider
        self._result_handler = result_handler
        self._scrim_state_provider = scrim_state_provider
        self._voice_operation_service = voice_operation_service

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

        setup_scrim = Scrim(None, game, ScrimState.SETTING_UP)
        message = await self._response_builder.send(ctx, displayable=setup_scrim)
        scrim = await self._scrim_converter.create_scrim(message, game)
        await message.add_reaction(emoji="\U0001F3AE")  # video game controller
        await message.add_reaction(emoji="\U0001F441")  # eye
        await self._response_builder.edit(message, displayable=scrim)

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

        async with self._scrim_converter.fetch_scrim(ctx.channel.id) as scrim:
            await ctx.message.delete()
            state = self._scrim_state_provider.resolve_from_key(scrim.state).transition(scrim, ScrimState.LOCKED)
            message = await ctx.channel.get_message(scrim.message_id)
            await self._response_builder.edit(message, displayable=scrim)
            await message.clear_reactions()
            await _add_team_reactions(scrim, state, message)

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

        async with self._scrim_converter.fetch_scrim(ctx.channel.id) as scrim:
            message = await ctx.channel.get_message(scrim.message_id)
            await criteria.create_teams(scrim, message)
            await ctx.message.delete()
            await self._response_builder.edit(message, displayable=scrim)

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

        async with self._scrim_converter.fetch_scrim(ctx.channel.id) as scrim:
            await ctx.message.delete()
            target_state = ScrimState.STARTED
            if move_voice and not await self._voice_operation_service.try_move_to_voice(ctx.guild, scrim):
                target_state = ScrimState.VOICE_WAIT
            self._scrim_state_provider.resolve_from_key(scrim.state).transition(scrim, target_state)
            message = await ctx.channel.get_message(scrim.message_id)
            await message.clear_reactions()
            await self._response_builder.edit(message, displayable=scrim)

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
        self._result_handler.save_result(ctx, winner)
        self._scrims_manager.drop(scrim)
        self._participant_provider.drop_participants(
            *[participant.user_id for participant in scrim.teams_manager.all_participants])

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
        self._participant_provider.drop_participants(
            *[participant.user_id for participant in scrim.teams_manager.all_participants])


def setup(client: ScrimBotClient):
    client.add_cog(ScrimCommands())
    print(f"Using cog {__name__}, with version {__version__}")
