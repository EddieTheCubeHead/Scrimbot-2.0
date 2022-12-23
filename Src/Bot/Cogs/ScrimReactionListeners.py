__version__ = "0.1"
__author__ = "Eetu Asikainen"

import re

from discord import Reaction, Member, Message
from discord.ext import commands
from discord.ext.commands import CommandError
from hintedi import HinteDI

from Src.Bot.Cogs.Helpers.ScrimTeamOperationService import ScrimTeamOperationService
from Src.Bot.Converters.ScrimConverter import ScrimConverter
from Src.Bot.Converters.UserConverter import UserConverter
from Src.Bot.DataClasses.Scrim import ScrimState, Scrim
from Src.Bot.DataClasses.Team import PARTICIPANTS, SPECTATORS, QUEUE
from Src.Bot.DataClasses.User import User
from Src.Bot.EmbedSystem.NewScrimEmbedBuilder import NewScrimEmbedBuilder
from Src.Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Src.Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Src.Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Src.Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Src.Bot.Exceptions.BotInvalidReactionJoinException import BotInvalidReactionJoinException
from Src.Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Src.Bot.Logic.ScrimManager import ScrimManager
from Src.Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Src.Bot.Core.ScrimBotClient import ScrimBotClient
from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
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


async def _try_remove_old_reaction(message: Message, new_team: int, user: Member):
    for reaction in message.reactions:
        if re.match(rf"^(?!{new_team})[1-9]\u20E3$", str(reaction.emoji)):
            try:
                await reaction.remove(user)
            except CommandError:
                pass


def _assert_room_in_team(user: User, scrim: Scrim, team_name: str):
    team = next((team for team in scrim.teams if team.team.name == team_name), None)
    if team is not None and team.max_size != 0 and len(team.team.members) >= team.max_size:
        raise BotInvalidJoinException(user, team_name, "team is already full")


class ScrimReactionListeners(commands.Cog):
    """A cog responsive for tracking the reaction-based UI of the scrims

    Listeners
    ---------
    scrim_reaction_add_listener(react, user)
        A listener for processing added reactions

    scrim_reaction_remove_listener(react, user)
        A listener for processing removed reactions
    """

    @HinteDI.inject
    def __init__(self, embed_builder: NewScrimEmbedBuilder, user_converter: UserConverter,
                 scrim_converter: ScrimConverter, teams_service: ScrimTeamOperationService):
        self._embed_builder = embed_builder
        self._user_converter = user_converter
        self._scrim_converter = scrim_converter
        self._teams_service = teams_service

    @commands.Cog.listener("on_reaction_add")
    async def scrim_reaction_add_listener(self, react: Reaction, member: Member):
        """A listener responsible for processing reactions added to scrim messages

        args
        ----

        :param react: The reaction associated with the event
        :type react: discord.Reaction
        :param member: The user associated with the reaction event
        :type member: discord.Member
        """
        if member.bot:
            return

        async with self._scrim_converter.fetch_scrim(react.message.channel.id) as scrim:
            if not scrim:
                return
            await self.handle_reaction_add(scrim, react, member)

        await self._embed_builder.edit(react.message, displayable=scrim)

    async def handle_reaction_add(self, scrim: Scrim, react: Reaction, member: Member):
        try:
            user = self._user_converter.get_user(member.id)
            if react.emoji == "\U0001F3AE" and scrim.state == ScrimState.LFP:
                self._try_add_to_team(scrim, user, PARTICIPANTS)

            elif react.emoji == "\U0001F441" and scrim.state == ScrimState.LFP:
                self._try_add_to_team(scrim, user, SPECTATORS)

            elif re.match(r"^[1-9]\u20E3$", str(react.emoji)) and scrim.state == ScrimState.LOCKED:
                new_team = int(str(react.emoji[0]))
                _assert_room_in_team(user, scrim, f"Team {new_team}")
                self._remove_from_team(scrim, user)
                self._try_add_to_team(scrim, user, f"Team {int(str(react.emoji[0]))}")
                await _try_remove_old_reaction(react.message, new_team, member)

            else:
                await react.remove(member)

        except BotInvalidJoinException as exception:
            exception_reason = f"User '{member.id}' could not join team '{exception.team}' with reaction {react}" \
                               f" because they are {exception.reason}."
            await BotInvalidReactionJoinException(member, react, exception_reason).resolve()

        except BotAlreadyParticipantException:
            exception_reason = f"User '{member.id}' could not join the scrim with reaction {react}" \
                               f" because they are already a participant in another scrim."
            await BotInvalidReactionJoinException(member, react, exception_reason).resolve()

    def _try_add_to_team(self, scrim: Scrim, user: User, team_name: str):
        if self._user_converter.is_in_another_scrim(user, scrim):
            raise BotAlreadyParticipantException(user)

        if user.user_id in [member.user_id for team in scrim.teams for member in team.team.members] \
           and team_name in (PARTICIPANTS, SPECTATORS, QUEUE):

            raise BotInvalidJoinException(user, team_name, "already participating in the scrim")
        self._teams_service.add_to_team(scrim, user, team_name)

    def _remove_from_team(self, scrim: Scrim, user: User):
        self._teams_service.remove_from_team(scrim, user)

    @commands.Cog.listener("on_reaction_remove")
    async def scrim_reaction_remove_listener(self, react: Reaction, member: Member):
        """A listener responsible for processing reactions removed from scrim messages

        args
        ----

        :param react: The reaction associated with the event
        :type react: discord.Reaction
        :param member: The user associated with the reaction event
        :type member: discord.Member
        """

        if member.bot:
            return

        async with self._scrim_converter.fetch_scrim(react.message.channel.id) as scrim:
            if not scrim:
                return
            await self.handle_reaction_remove(scrim, react, member)

        await self._embed_builder.edit(react.message, displayable=scrim)

    async def handle_reaction_remove(self, scrim: Scrim, react: Reaction, member: Member):
        try:
            user = self._user_converter.get_user(member.id)
            if react.emoji in ("\U0001F3AE", "\U0001F441") and scrim.state == ScrimState.LFP:
                self._remove_from_team(scrim, user)

            elif re.match(r"^[1-9]\u20E3$", str(react.emoji)) and scrim.state == ScrimState.LOCKED:
                self._remove_from_team(scrim, user)
                self._try_add_to_team(scrim, user, PARTICIPANTS)

        except BotInvalidPlayerRemoval as exception:
            exception.resolve()


def setup(client: ScrimBotClient):
    client.add_cog(ScrimReactionListeners())
    print(f"Using cog {__name__}, with version {__version__}")
