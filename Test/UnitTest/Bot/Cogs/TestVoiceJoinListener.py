__version__ = "ver"
__author__ = "Eetu Asikainen"

import datetime
from unittest.mock import MagicMock, AsyncMock

from Bot.Cogs.VoiceJoinListener import VoiceJoinListener
from Bot.DataClasses.User import User
from Bot.EmbedSystem.ScrimStates.scrim_states import VOICE_WAIT
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestVoiceJoinListener(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_participant_manager = MagicMock()
        self.mock_waiting_scrim_service = MagicMock()
        self.mock_response_builder = AsyncMock()
        self.listener = VoiceJoinListener(self.mock_participant_manager, self.mock_waiting_scrim_service,
                                          self.mock_response_builder)

    async def test_scrim_player_voice_state_change_listener_when_non_member_joins_then_nothing_done(self):
        self.mock_participant_manager.try_get_participant.return_value = None
        await self.listener.scrim_player_voice_state_change_listener(MagicMock(), MagicMock(), MagicMock())
        self.mock_waiting_scrim_service.get_scrim.assert_not_called()

    async def test_scrim_player_voice_state_change_listener_when_scrim_member_joins_voice_then_scrim_notified(self):
        mock_participant = MagicMock()
        mock_participant.id = self.id_generator.generate_viable_id()
        self.mock_participant_manager.try_get_participant.return_value = mock_participant
        mock_scrim = AsyncMock()
        mock_scrim.state = VOICE_WAIT
        mock_scrim.message.channel.guild.id = self.id_generator.generate_viable_id()
        self.mock_waiting_scrim_service.get_scrim.return_value = mock_scrim
        mock_scrim.teams_manager.all_participants = {User(mock_participant.id)}
        mock_before = MagicMock()
        mock_after = MagicMock()
        mock_before.channel = None
        mock_after.channel.guild.id = mock_scrim.message.channel.guild.id
        await self.listener.scrim_player_voice_state_change_listener(mock_participant, mock_before, mock_after)
        mock_scrim.start_with_voice.assert_called()
        self.mock_waiting_scrim_service.unregister.assert_called_with(mock_scrim)
        self.mock_response_builder.edit.assert_called_with(mock_scrim.message, displayable=mock_scrim)
        mock_scrim.message.clear_reactions.assert_called()

    async def test_scrim_player_voice_state_change_listener_when_leaves_voice_then_nothing_happens(self):
        mock_participant = MagicMock()
        mock_participant.id = self.id_generator.generate_viable_id()
        self.mock_participant_manager.try_get_participant.return_value = mock_participant
        mock_scrim = AsyncMock()
        mock_scrim.state = VOICE_WAIT
        self.mock_waiting_scrim_service.get_scrim.return_value = mock_scrim
        mock_scrim.teams_manager.all_participants = {User(mock_participant.id)}
        mock_before = MagicMock()
        mock_after = MagicMock()
        mock_before.channel = None
        mock_after.channel = None
        await self.listener.scrim_player_voice_state_change_listener(mock_participant, mock_before, mock_after)
        self.mock_waiting_scrim_service.get_scrim.assert_not_called()

    async def test_scrim_player_voice_state_change_listener_when_member_joins_other_guild_then_not_notified(self):
        mock_participant = MagicMock()
        mock_participant.id = self.id_generator.generate_viable_id()
        self.mock_participant_manager.try_get_participant.return_value = mock_participant
        mock_scrim = AsyncMock()
        mock_scrim.state = VOICE_WAIT
        mock_scrim.message.channel.guild.id = self.id_generator.generate_viable_id()
        self.mock_waiting_scrim_service.get_scrim.return_value = mock_scrim
        mock_scrim.teams_manager.all_participants = {User(mock_participant.id)}
        mock_before = MagicMock()
        mock_after = MagicMock()
        mock_before.channel = None
        mock_after.channel.guild.id = self.id_generator.generate_viable_id()
        await self.listener.scrim_player_voice_state_change_listener(mock_participant, mock_before, mock_after)
        mock_scrim.start_with_voice.assert_not_called()

    async def test_scrim_player_voice_state_change_listener_when_member_was_in_guild_voice_then_not_notified(self):
        mock_participant = MagicMock()
        mock_participant.id = self.id_generator.generate_viable_id()
        self.mock_participant_manager.try_get_participant.return_value = mock_participant
        mock_scrim = AsyncMock()
        mock_scrim.state = VOICE_WAIT
        mock_scrim.message.channel.guild.id = self.id_generator.generate_viable_id()
        self.mock_waiting_scrim_service.get_scrim.return_value = mock_scrim
        mock_scrim.teams_manager.all_participants = {User(mock_participant.id)}
        mock_before = MagicMock()
        mock_after = MagicMock()
        mock_before.channel.guild.id = mock_scrim.message.channel.guild.id
        await self.listener.scrim_player_voice_state_change_listener(mock_participant, mock_before, mock_after)
        mock_scrim.start_with_voice.assert_not_called()

    async def test_prune_observers_when_called_then_waiting_scrim_service_prune_called_and_returned_scrims_edited(self):
        mock_pruned = MagicMock()
        mock_pruned.message = "test"
        pruned = [mock_pruned]
        self.mock_waiting_scrim_service.prune.return_value = pruned
        await self.listener.prune_observers()
        self.mock_waiting_scrim_service.prune.assert_called()
        for mock_scrim in pruned:
            self.mock_response_builder.edit.assert_called_with("test", displayable=mock_scrim)

