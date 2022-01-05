__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock, call

from discord import Emoji, Reaction

from Bot.Cogs.ScrimReactionListeners import ScrimReactionListeners
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Game import Game
from Bot.EmbedSystem.ScrimStates.scrim_states import LFP, LOCKED
from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Bot.Exceptions.BotInvalidReactionJoinException import BotInvalidReactionJoinException
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class _RemovedDependencySentinel:
    pass


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
        self.cog = ScrimReactionListeners(self.active_scrims_manager, self.embed_builder, self.user_converter)
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

    async def test_on_reaction_add_given_invalid_join_caught_then_exception_logged_and_reaction_removed(self):
        self.scrim.state = LFP
        mock_team = MagicMock()
        original_exception = BotInvalidJoinException(self.mock_user, mock_team, "Reason")
        self.scrim.teams_manager.add_player.side_effect = original_exception
        players_joining_reaction = AsyncMock()
        players_joining_reaction.emoji = "\U0001F441"
        system_logger = MagicMock()
        original_dependency = BotDependencyInjector.dependencies.pop(BotSystemLogger, _RemovedDependencySentinel())
        BotDependencyInjector.dependencies[BotSystemLogger] = system_logger
        try:
            await self.cog.scrim_reaction_add_listener(players_joining_reaction, self.mock_member)
        finally:
            if not isinstance(original_dependency, _RemovedDependencySentinel):
                BotDependencyInjector.dependencies[BotSystemLogger] = original_dependency
            else:
                BotDependencyInjector.dependencies.pop(BotSystemLogger)
        players_joining_reaction.remove.assert_called_with(self.mock_member)
        system_logger.debug.assert_called_with(f"An exception occurred during bot operation: User "
                                               f"'{self.mock_member.id}' could not join team "
                                               f"'{original_exception.team.name}' with reaction "
                                               f"{players_joining_reaction} because they are Reason.")

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

