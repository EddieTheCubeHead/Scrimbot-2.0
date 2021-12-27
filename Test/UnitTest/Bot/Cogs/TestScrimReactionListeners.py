__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock, call

from discord import Emoji, Reaction

from Bot.Cogs.ScrimReactionListeners import ScrimReactionListeners
from Bot.DataClasses.Game import Game
from Bot.DataClasses.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimReactionListeners(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.active_scrims_manager = MagicMock()
        self.scrim = MagicMock()
        self.active_scrims_manager.try_get_scrim = self.get_scrim
        self.embed_builder = AsyncMock()
        self.user_converter = MagicMock()
        self.cog = ScrimReactionListeners(self.active_scrims_manager, self.embed_builder, self.user_converter)
        self.cog._inject(MagicMock())

    def get_scrim(self, channel_id):
        return self.scrim

    async def test_on_reaction_add_given_players_reaction_then_user_added_to_players_and_message_edited(self):
        mock_message = AsyncMock()
        mock_message.id = self.id_generator.generate_viable_id()
        players_joining_reaction = Reaction(data={}, message=mock_message, emoji="\U0001F3AE")
        self.scrim.state = ScrimState.LFP
        mock_member = MagicMock()
        mock_member.bot = False
        mock_member.id = self.id_generator.generate_viable_id()
        mock_user = MagicMock()
        self.user_converter.get_user.return_value = mock_user
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, mock_member)
        self.scrim.teams_manager.add_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, mock_user)
        self.embed_builder.edit.assert_called_with(mock_message, displayable=self.scrim)

    async def test_on_reaction_add_given_spectator_reaction_then_user_added_to_spectators_and_message_edited(self):
        mock_message = AsyncMock()
        mock_message.id = self.id_generator.generate_viable_id()
        players_joining_reaction = Reaction(data={}, message=mock_message, emoji="\U0001F441")
        self.scrim.state = ScrimState.LFP
        mock_member = MagicMock()
        mock_member.bot = False
        mock_member.id = self.id_generator.generate_viable_id()
        mock_user = MagicMock()
        self.user_converter.get_user.return_value = mock_user
        await self.cog.scrim_reaction_add_listener(players_joining_reaction, mock_member)
        self.scrim.teams_manager.add_player.assert_called_with(ScrimTeamsManager.SPECTATORS, mock_user)
        self.embed_builder.edit.assert_called_with(mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_players_reaction_then_player_removed_and_message_edited(self):
        mock_message = AsyncMock()
        mock_message.id = self.id_generator.generate_viable_id()
        players_joining_reaction = Reaction(data={}, message=mock_message, emoji="\U0001F3AE")
        self.scrim.state = ScrimState.LFP
        mock_member = MagicMock()
        mock_member.bot = False
        mock_member.id = self.id_generator.generate_viable_id()
        mock_user = MagicMock()
        self.user_converter.get_user.return_value = mock_user
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, mock_member)
        self.scrim.teams_manager.remove_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, mock_user)
        self.embed_builder.edit.assert_called_with(mock_message, displayable=self.scrim)

    async def test_on_reaction_remove_given_spectators_reaction_then_spectator_removed_and_message_edited(self):
        mock_message = AsyncMock()
        mock_message.id = self.id_generator.generate_viable_id()
        players_joining_reaction = Reaction(data={}, message=mock_message, emoji="\U0001F441")
        self.scrim.state = ScrimState.LFP
        mock_member = MagicMock()
        mock_member.bot = False
        mock_member.id = self.id_generator.generate_viable_id()
        mock_user = MagicMock()
        self.user_converter.get_user.return_value = mock_user
        await self.cog.scrim_reaction_remove_listener(players_joining_reaction, mock_member)
        self.scrim.teams_manager.remove_player.assert_called_with(ScrimTeamsManager.SPECTATORS, mock_user)
        self.embed_builder.edit.assert_called_with(mock_message, displayable=self.scrim)

