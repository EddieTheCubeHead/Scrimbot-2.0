__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import AsyncMock, MagicMock, call

from discord import Emoji, Reaction
from discord.ext.commands import CommandError

from Src.Bot.Cogs.ScrimReactionListeners import ScrimReactionListeners
from Src.Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Scrim import ScrimState
from Src.Bot.DataClasses.Team import SPECTATORS, PARTICIPANTS, QUEUE
from Src.Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Src.Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Src.Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Src.Bot.Exceptions.BotInvalidReactionJoinException import BotInvalidReactionJoinException
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Test.Utils.TestHelpers.bot_dependency_patcher import mock_dependency


def _create_team(name: str):
    participant_team = MagicMock()
    team = MagicMock()
    team.name = name
    participant_team.team = team
    participant_team.max_size = 0
    return participant_team


class TestScrimReactionListeners(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.scrim = MagicMock()
        self.scrim.teams = [_create_team(name) for name in (PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")]
        self.embed_builder = AsyncMock()
        self.user_converter = MagicMock()
        self.user_converter.is_in_another_scrim.return_value = False
        self.scrim_converter = MagicMock()
        self.scrim_converter.fetch_scrim.return_value.__aenter__.return_value = self.scrim
        self.teams_service = MagicMock()
        self.cog = ScrimReactionListeners(self.embed_builder, self.user_converter, self.scrim_converter,
                                          self.teams_service)
        self.cog._inject(MagicMock())
        self.mock_message = AsyncMock()
        self.mock_message.id = self.id_generator.generate_viable_id()
        self.mock_member = MagicMock()
        self.mock_member.bot = False
        self.mock_member.id = self.id_generator.generate_viable_id()
        self.mock_user = MagicMock()
        self.user_converter.get_user.return_value = self.mock_user

    async def test_on_reaction_add_given_reacted_by_bot_then_nothing_happens(self):
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        self.mock_member.bot = True
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.scrim_converter.fetch_scrim.assert_not_called()

    async def test_on_reaction_add_given_players_reaction_then_user_added_to_players_and_message_edited(self):
        self.scrim.state = ScrimState.LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, PARTICIPANTS)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_spectator_reaction_then_user_added_to_spectators_and_message_edited(self):
        self.scrim.state = ScrimState.LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F441")
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, SPECTATORS)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_team_reaction_then_user_added_to_correct_team_and_message_edited(self):
        self.scrim.state = ScrimState.LOCKED
        for team in range(1, 10):
            with self.subTest(f"Adding team joining reaction '{team}'"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"{team}\u20E3")
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, f"Team {team}")
                self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_old_reaction_removal_fails_then_exception_handled(self):
        self.scrim.state = ScrimState.LOCKED
        invalid_removal_reaction = MagicMock()
        invalid_removal_reaction.emoji = "1\u20E3"
        invalid_removal_reaction.remove.side_effect = CommandError()
        self.mock_message.reactions = [invalid_removal_reaction]
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"2\u20E3")
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.teams_service.remove_from_team.assert_called_with(self.scrim, self.mock_user)
        self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, "Team 2")
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_player_in_another_team_then_original_reaction_removed(self):
        self.scrim.state = ScrimState.LOCKED
        for team in range(1, 10):
            with self.subTest(f"Removing old reaction while adding team joining reaction '{team}'"):
                original_joining_reaction = AsyncMock()
                original_joining_reaction.emoji = f"{(team + 1) % 9 + 1}\u20E3"
                original_joining_reaction.users.return_value = [self.mock_member]
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"{team}\u20E3")
                self.mock_message.reactions = [original_joining_reaction]
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                original_joining_reaction.remove.assert_called_with(self.mock_member)

    async def test_on_reaction_add_given_multi_scrim_join_caught_then_exception_logged_and_reaction_removed(self):
        self.scrim.state = ScrimState.LFP
        self.user_converter.is_in_another_scrim.return_value = True
        mock_team = SPECTATORS
        players_joining_reaction = AsyncMock()
        players_joining_reaction.emoji = "\U0001F441"
        system_logger = MagicMock()
        with mock_dependency(BotSystemLogger, system_logger):
            await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        players_joining_reaction.remove.assert_called_with(self.mock_member)
        system_logger.debug.assert_called_with(f"An exception occurred during bot operation: User "
                                               f"'{self.mock_member.id}' could not join the scrim with reaction "
                                               f"{players_joining_reaction} because they are already a participant in "
                                               f"another scrim.")

    async def test_on_reaction_add_when_joining_participants_or_spectators_then_participant_manager_updated(self):
        emojis = ("\U0001F441", "\U0001F3AE")
        teams = (SPECTATORS, PARTICIPANTS)
        self.scrim.state = ScrimState.LFP
        for emoji, team in zip(emojis, teams):
            with self.subTest(f"Joining a scrim with reaction ({team})"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=emoji)
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, team)

    async def test_on_reaction_add_when_joining_game_teams_then_participant_manager_not_updated(self):
        emojis = ("1\u20E3", "2\u20E3", "3\u20E3", "4\u20E3")
        teams = ("Team 1", "Team 2", "Team 3", "Team 4")
        self.scrim.state = ScrimState.LOCKED
        for emoji, team in zip(emojis, teams):
            with self.subTest(f"Joining a scrim with reaction ({team})"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=emoji)
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, team)

    async def test_on_reaction_remove_given_reacted_by_bot_then_nothing_happens(self):
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        self.mock_member.bot = True
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.scrim_converter.fetch_scrim.assert_not_called()

    async def test_on_reaction_remove_given_players_reaction_then_player_removed_and_message_edited(self):
        self.scrim.state = ScrimState.LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.teams_service.remove_from_team.assert_called_with(self.scrim, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_spectators_reaction_then_spectator_removed_and_message_edited(self):
        self.scrim.state = ScrimState.LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F441")
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.teams_service.remove_from_team.assert_called_with(self.scrim, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_team_reaction_then_user_removed_from_team_and_message_edited(self):
        self.scrim.state = ScrimState.LOCKED
        for team in range(1, 10):
            with self.subTest(f"Adding team joining reaction '{team}'"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"{team}\u20E3")
                await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
                self.teams_service.remove_from_team.assert_called_with(self.scrim, self.mock_user)
                self.teams_service.add_to_team.assert_called_with(self.scrim, self.mock_user, PARTICIPANTS)
                self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)
