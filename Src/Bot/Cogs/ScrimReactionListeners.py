__version__ = "0.1"
__author__ = "Eetu Asikainen"

import re

from discord import Reaction, Member, DiscordException, Message
from discord.ext import commands
from discord.ext.commands import CommandError

from Bot.Converters.UserConverter import UserConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Bot.EmbedSystem.ScrimStates.scrim_states import *
from Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Bot.Exceptions.BotInvalidReactionJoinException import BotInvalidReactionJoinException
from Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.DataClasses.ScrimChannel import ScrimChannel


async def _try_remove_old_reaction(message: Message, new_team: int, user: Member):
    for reaction in message.reactions:
        if re.match(rf"^(?!{new_team})[1-9]\u20E3$", str(reaction.emoji)):
            try:
                await reaction.remove(user)
            except CommandError:
                pass


class ScrimReactionListeners(commands.Cog):
    """A cog responsive for tracking the reaction-based UI of the scrims

    Listeners
    ---------
    scrim_reaction_add_listener(react, user)
        A listener for processing added reactions

    scrim_reaction_remove_listener(react, user)
        A listener for processing removed reactions
    """

    @BotDependencyInjector.inject
    def __init__(self, scrim_manager: ActiveScrimsManager, embed_builder: ScrimEmbedBuilder,
                 user_converter: UserConverter, participant_manager: ScrimParticipantProvider):
        self.scrim_manager = scrim_manager
        self.embed_builder = embed_builder
        self.user_converter = user_converter
        self.participant_manager = participant_manager

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

        scrim = self.scrim_manager.try_get_scrim(react.message.channel.id)
        if not scrim:
            return

        try:
            user = self.user_converter.get_user(member.id)
            if react.emoji == "\U0001F3AE" and scrim.state == LFP:
                self.participant_manager.ensure_not_participant(member)
                scrim.teams_manager.add_player(ScrimTeamsManager.PARTICIPANTS, user)
                self.participant_manager.try_add_participant(member)

            elif react.emoji == "\U0001F441" and scrim.state == LFP:
                self.participant_manager.ensure_not_participant(member)
                scrim.teams_manager.add_player(ScrimTeamsManager.SPECTATORS, user)
                self.participant_manager.try_add_participant(member)

            elif re.match(r"^[1-9]\u20E3$", str(react.emoji)) and scrim.state == LOCKED:
                new_team = int(str(react.emoji[0]))
                scrim.teams_manager.set_team(new_team - 1, user)
                await _try_remove_old_reaction(react.message, new_team, member)

            elif react.emoji == "\U0001F451" and scrim.state == CAPS_PREP:
                await scrim.add_captain(member)

            else:
                await react.remove(member)

        except BotInvalidJoinException as exception:
            exception_reason = f"User '{member.id}' could not join team '{exception.team.name}' with reaction {react}" \
                               f" because they are {exception.reason}."
            await BotInvalidReactionJoinException(member, react, exception_reason).resolve()

        except BotAlreadyParticipantException as exception:
            exception_reason = f"User '{member.id}' could not join the scrim with reaction {react}" \
                               f" because they are already a participant in another scrim."
            await BotInvalidReactionJoinException(member, react, exception_reason).resolve()

        await self.embed_builder.edit(react.message, displayable=scrim)

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

        scrim = self.scrim_manager.try_get_scrim(react.message.channel.id)
        if not scrim:
            return

        try:
            user = self.user_converter.get_user(member.id)
            if react.emoji == "\U0001F3AE" and scrim.state == LFP:
                scrim.teams_manager.remove_player(ScrimTeamsManager.PARTICIPANTS, user)

            elif react.emoji == "\U0001F441" and scrim.state == LFP:
                scrim.teams_manager.remove_player(ScrimTeamsManager.SPECTATORS, user)

            elif re.match(r"^[1-9]\u20E3$", str(react.emoji)) and scrim.state == LOCKED:
                new_team = int(str(react.emoji[0]))
                scrim.teams_manager.remove_player(new_team - 1, user)
                scrim.teams_manager.add_player(ScrimTeamsManager.PARTICIPANTS, user)

            elif react.emoji == "\U0001F451" and scrim.state == CAPS_PREP:
                await scrim.remove_captain(user)

        except BotInvalidPlayerRemoval as exception:
            exception.resolve()

        await self.embed_builder.edit(react.message, displayable=scrim)


def setup(client: ScrimBotClient):
    """A method for adding the cog to the bot

    args
    ----

    :param client: The instance of the bot the cog should be added into
    :type client: ScrimBotClient
    """

    client.add_cog(ScrimReactionListeners())
    print(f"Using cog {__name__}, with version {__version__}")
