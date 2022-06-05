__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock, call

from discord import Emoji, Reaction
from discord.ext.commands import CommandError

from Bot.Cogs.ScrimReactionListeners import ScrimReactionListeners
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Game import Game
from Bot.EmbedSystem.ScrimStates.scrim_states import LFP, LOCKED
from Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Bot.Exceptions.BotInvalidReactionJoinException import BotInvalidReactionJoinException
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Test.Utils.TestHelpers.bot_dependency_patcher import mock_dependency


class TestScrimReactionListeners(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.active_scrims_manager = MagicMock()
        self.scrim = MagicMock()
        self.scrim_fetched = False
        self.active_scrims_manager.try_get_scrim = self.get_scrim
        self.embed_builder = AsyncMock()
        self.user_converter = MagicMock()
        self.participant_manager = MagicMock()
        self.cog = ScrimReactionListeners(self.active_scrims_manager, self.embed_builder, self.user_converter,
                                          self.participant_manager)
        self.cog._inject(MagicMock())
        self.mock_message = AsyncMock()
        self.mock_message.id = self.id_generator.generate_viable_id()
        self.mock_member = MagicMock()
        self.mock_member.bot = False
        self.mock_member.id = self.id_generator.generate_viable_id()
        self.mock_user = MagicMock()
        self.user_converter.get_user.return_value = self.mock_user

    def get_scrim(self, channel_id):
        self.scrim_fetched = True
        return self.scrim

    async def test_on_reaction_add_given_reacted_by_bot_then_nothing_happens(self):
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        self.mock_member.bot = True
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.assertFalse(self.scrim_fetched)

    async def test_on_reaction_add_given_no_scrim_then_nothing_happens(self):
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        self.mock_member.bot = False
        self.scrim = None
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.assertTrue(self.scrim_fetched)

    async def test_on_reaction_add_given_players_reaction_then_user_added_to_players_and_message_edited(self):
        self.scrim.state = LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.scrim.teams_manager.add_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_spectator_reaction_then_user_added_to_spectators_and_message_edited(self):
        self.scrim.state = LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F441")
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.scrim.teams_manager.add_player.assert_called_with(ScrimTeamsManager.SPECTATORS, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_team_reaction_then_user_added_to_correct_team_and_message_edited(self):
        self.scrim.state = LOCKED
        for team in range(1, 10):
            with self.subTest(f"Adding team joining reaction '{team}\u20E3'"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"{team}\u20E3")
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                self.scrim.teams_manager.set_team.assert_called_with(team - 1, self.mock_user)
                self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_old_reaction_removal_fails_then_exception_handled(self):
        self.scrim.state = LOCKED
        invalid_removal_reaction = MagicMock()
        invalid_removal_reaction.emoji = "1\u20E3"
        invalid_removal_reaction.remove.side_effect = CommandError()
        self.mock_message.reactions = [invalid_removal_reaction]
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"2\u20E3")
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        self.scrim.teams_manager.set_team.assert_called_with(2 - 1, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_player_in_another_team_then_original_reaction_removed(self):
        self.scrim.state = LOCKED
        for team in range(1, 10):
            with self.subTest(f"Removing old reaction while adding team joining reaction '{team}\u20E3'"):
                original_joining_reaction = AsyncMock()
                original_joining_reaction.emoji = f"{(team + 1) % 9 + 1}\u20E3"
                original_joining_reaction.users.return_value = [self.mock_member]
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"{team}\u20E3")
                self.mock_message.reactions = [original_joining_reaction]
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                original_joining_reaction.remove.assert_called_with(self.mock_member)

    async def test_on_reaction_add_given_multi_scrim_join_caught_then_exception_logged_and_reaction_removed(self):
        self.scrim.state = LFP
        players_joining_reaction = AsyncMock()
        players_joining_reaction.emoji = "\U0001F441"
        system_logger = MagicMock()
        with mock_dependency(BotSystemLogger, system_logger):
            original_exception = BotAlreadyParticipantException(self.mock_user, system_logger)
            self.participant_manager.ensure_not_participant.side_effect = original_exception
            await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        players_joining_reaction.remove.assert_called_with(self.mock_member)
        system_logger.debug.assert_called_with(f"An exception occurred during bot operation: "
                                               f"User '{self.mock_member.id}' could not join the scrim with reaction "
                                               f"{players_joining_reaction} because they are already a participant in "
                                               f"another scrim.")

    async def test_on_reaction_add_given_invalid_join_caught_then_exception_logged_and_reaction_removed(self):
        self.scrim.state = LFP
        mock_team = MagicMock()
        players_joining_reaction = AsyncMock()
        players_joining_reaction.emoji = "\U0001F441"
        system_logger = MagicMock()
        with mock_dependency(BotSystemLogger, system_logger):
            original_exception = BotInvalidJoinException(self.mock_user, mock_team, "Reason")
            self.scrim.teams_manager.add_player.side_effect = original_exception
            await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        players_joining_reaction.remove.assert_called_with(self.mock_member)
        system_logger.debug.assert_called_with(f"An exception occurred during bot operation: User "
                                               f"'{self.mock_member.id}' could not join team "
                                               f"'{original_exception.team.name}' with reaction "
                                               f"{players_joining_reaction} because they are Reason.")

    async def test_on_reaction_add_when_joining_participants_or_spectators_then_participant_manager_updated(self):
        emojis = ("\U0001F441", "\U0001F3AE")
        self.scrim.state = LFP
        for emoji in emojis:
            with self.subTest(f"Joining a scrim with reaction {emoji}"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=emoji)
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                self.participant_manager.ensure_not_participant.assert_called_with(self.mock_member)
                self.participant_manager.try_add_participant.assert_called_with(self.mock_member)

    async def test_on_reaction_add_when_joining_game_teams_then_participant_manager_not_updated(self):
        emojis = ("\U0001F451", "1\u20E3", "2\u20E3", "3\u20E3", "4\u20E3")
        self.scrim.state = LFP
        for emoji in emojis:
            with self.subTest(f"Joining a scrim with reaction {emoji}"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=emoji)
                await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
                self.participant_manager.ensure_not_participant.assert_not_called()
                self.participant_manager.try_add_participant.assert_not_called()

    async def test_on_reaction_remove_given_reacted_by_bot_then_nothing_happens(self):
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        self.mock_member.bot = True
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.assertFalse(self.scrim_fetched)

    async def test_on_reaction_remove_given_no_scrim_then_nothing_happens(self):
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        self.mock_member.bot = False
        self.scrim = None
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.assertTrue(self.scrim_fetched)

    async def test_on_reaction_remove_given_players_reaction_then_player_removed_and_message_edited(self):
        self.scrim.state = LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F3AE")
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.scrim.teams_manager.remove_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_spectators_reaction_then_spectator_removed_and_message_edited(self):
        self.scrim.state = LFP
        players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji="\U0001F441")
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        self.scrim.teams_manager.remove_player.assert_called_with(ScrimTeamsManager.SPECTATORS, self.mock_user)
        self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_team_reaction_then_user_removed_from_team_and_message_edited(self):
        self.scrim.state = LOCKED
        for team in range(1, 10):
            with self.subTest(f"Adding team joining reaction '{team}\u20E3'"):
                players_joining_reaction = Reaction(data={}, message=self.mock_message, emoji=f"{team}\u20E3")
                await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
                self.scrim.teams_manager.remove_player.assert_called_with(team - 1, self.mock_user)
                self.scrim.teams_manager.add_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, self.mock_user)
                self.embed_builder.edit.assert_called_with(self.mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_invalid_removal_caught_then_exception_logged(self):
        self.scrim.state = LFP
        mock_team = MagicMock()
        players_joining_reaction = AsyncMock()
        players_joining_reaction.emoji = "\U0001F441"
        system_logger = MagicMock()
        with mock_dependency(BotSystemLogger, system_logger):
            original_exception = BotInvalidPlayerRemoval(self.mock_user, mock_team)
            self.scrim.teams_manager.remove_player.side_effect = original_exception
            await self.cog.scrim_reaction_remove_listener(players_joining_reaction, self.mock_member)
        system_logger.debug.assert_called_with(f"An exception occurred during bot operation: Tried to remove player "
                                               f"<@{self.mock_user.user_id}> from team '{mock_team.name}' even though "
                                               f"they are not a team member.")

