__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from Src.Bot.Cogs.ScrimCommands import ScrimCommands
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Scrim import ScrimState
from Src.Bot.DataClasses.User import User
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimCommands(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.scrim_channel_converter = MagicMock()
        self.response_builder = AsyncMock()
        self.settings_service = MagicMock()
        self.scrim_converter = AsyncMock()
        self.active_scrims_manager = MagicMock()
        self.waiting_scrim_service = MagicMock()
        self.participant_provider = MagicMock()
        self.result_handler = MagicMock()
        self.state_provider = MagicMock()
        self.mock_scrim = MagicMock()
        self.mock_voice_operation_service = AsyncMock()

        mock_context_manager = MagicMock()
        mock_context_manager.return_value.__aenter__.return_value = self.mock_scrim
        self.scrim_converter.fetch_scrim = mock_context_manager

        self.cog = ScrimCommands(self.scrim_channel_converter, self.response_builder, self.settings_service,
                                 self.scrim_converter, self.active_scrims_manager, self.waiting_scrim_service,
                                 self.participant_provider, self.result_handler, self.state_provider,
                                 self.mock_voice_operation_service)
        self.cog._inject(MagicMock())

    async def test_scrim_given_called_with_game_then_scrim_with_game_created_and_embed_sent(self):
        game = Game("Test", "0xffffff", "icon_url", 5)
        ctx = AsyncMock()
        mock_message = AsyncMock()
        self.response_builder.send.return_value = mock_message
        ctx.scrim = None
        setup_scrim = MagicMock()
        mock_init = MagicMock()
        mock_init.return_value = setup_scrim
        result_scrim = MagicMock()
        self.scrim_converter.create_scrim.return_value = result_scrim
        await self.cog.scrim(ctx, game)
        self.response_builder.edit.assert_called_with(mock_message, displayable=result_scrim)

    async def test_scrim_given_called_with_game_then_team_joining_reactions_added(self):
        game = Game("Test", "0xffffff", "icon_url", 5)
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = None
        result_scrim = MagicMock()
        mock_scrim_channel = AsyncMock()
        scrim_message = AsyncMock()
        self.scrim_channel_converter.get_from_id.return_value = mock_scrim_channel
        self.scrim_converter.create_scrim.return_value = result_scrim
        self.response_builder.send.return_value = scrim_message
        await self.cog.scrim(ctx, game)
        calls = scrim_message.add_reaction.call_args_list
        self.assertEqual(calls[0], call(emoji="\U0001F3AE"))
        self.assertEqual(calls[1], call(emoji="\U0001F441"))

    async def test_scrim_given_called_successfully_then_message_saved_to_scrim(self):
        game = Game("Test", "0xffffff", "icon_url", 5)
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = None
        result_scrim = MagicMock()
        mock_scrim_channel = AsyncMock()
        scrim_message = AsyncMock()
        scrim_message.id = self.id_generator.generate_viable_id()
        self.scrim_channel_converter.get_from_id.return_value = mock_scrim_channel
        self.scrim_converter.create_scrim.return_value = result_scrim
        self.response_builder.send.return_value = scrim_message

        await self.cog.scrim(ctx, game)

        self.response_builder.edit.assert_called_with(scrim_message, displayable=result_scrim)

    async def test_lock_given_called_with_enough_participants_then_scrim_locked_and_message_edited(self):
        self.mock_scrim.state = ScrimState.LFP
        mock_message = AsyncMock()
        self.mock_scrim.message = mock_message
        mock_lfp_state = MagicMock()
        self.state_provider.resolve_from_key.return_value = mock_lfp_state
        ctx = AsyncMock()
        ctx.channel.get_message.return_value = mock_message
        ctx.scrim = self.mock_scrim

        await self.cog.lock(ctx)

        mock_lfp_state.transition.assert_called_with(self.mock_scrim, ScrimState.LOCKED)
        self.response_builder.edit.assert_called_with(mock_message, displayable=self.mock_scrim)
        ctx.message.delete.assert_called()

    async def test_lock_given_locked_then_scrim_joining_reactions_removed_and_team_joining_reactions_added(self):
        self.mock_scrim.state = ScrimState.LFP
        mock_message = AsyncMock()
        self.mock_scrim.message = mock_message
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = self.mock_scrim
        ctx.channel.get_message.return_value = mock_message
        mock_state = MagicMock()
        mock_transitioned_state = MagicMock()
        mock_state.transition.return_value = mock_transitioned_state
        self.state_provider.resolve_from_key.return_value = mock_state
        for team_count in range(2, 10):
            with self.subTest(f"Scrim locking reaction updates ({team_count} teams)"):
                mock_transitioned_state.get_game_teams.return_value = ["Team"] * team_count
                await self.cog.lock(ctx)
                mock_message.clear_reactions.assert_called()
                calls = mock_message.add_reaction.call_args_list
                for team in range(team_count):
                    self.assertEqual(calls[team], call(emoji=f"{team + 1}\u20E3"))
                mock_message.add_reaction.call_args_list = []

    async def test_start_given_no_move_voice_arg_then_player_moving_attempted(self):
        self.mock_scrim.state = ScrimState.LOCKED
        mock_state = MagicMock()
        mock_transitioned_state = MagicMock()
        mock_state.transition.return_value = mock_transitioned_state
        self.state_provider.resolve_from_key.return_value = mock_state
        ctx = AsyncMock()
        mock_message = AsyncMock()
        ctx.channel.get_message.return_value = mock_message
        self.mock_voice_operation_service.try_move_to_voice.return_value = False

        await self.cog.start(ctx)

        ctx.message.delete.assert_called()
        mock_state.transition.assert_called_with(self.mock_scrim, ScrimState.VOICE_WAIT)
        mock_message.clear_reactions.assert_called()
        self.response_builder.edit.assert_called_with(mock_message, displayable=self.mock_scrim)

    async def test_start_given_negative_move_voice_arg_then_started_without_moving(self):
        self.mock_scrim.state = ScrimState.LOCKED
        mock_state = MagicMock()
        mock_transitioned_state = MagicMock()
        mock_state.transition.return_value = mock_transitioned_state
        self.state_provider.resolve_from_key.return_value = mock_state
        ctx = AsyncMock()
        mock_message = AsyncMock()
        ctx.channel.get_message.return_value = mock_message

        await self.cog.start(ctx, False)

        ctx.message.delete.assert_called()
        mock_state.transition.assert_called_with(self.mock_scrim, ScrimState.STARTED)
        mock_message.clear_reactions.assert_called()
        self.response_builder.edit.assert_called_with(mock_message, displayable=self.mock_scrim)

    async def test_winner_given_team_name_then_team_made_winner(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        team_1 = MagicMock()
        team_2 = MagicMock()
        await self.cog.winner(ctx, [(team_1,), (team_2,)])
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([(team_1,), (team_2,)])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)

    async def test_winner_given_single_tuple_then_tie_result_set(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        team_1 = MagicMock()
        team_2 = MagicMock()
        await self.cog.winner(ctx, [(team_1, team_2)])
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([(team_1, team_2)])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)

    async def test_winner_given_empty_list_then_unregistered_result_set(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        participants = self._create_participants(10)
        ctx.scrim.teams_manager.all_participants = participants
        await self.cog.winner(ctx, [])
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        self.active_scrims_manager.drop.assert_called_with(mock_scrim)
        self.participant_provider.drop_participants.assert_called_with(
            *[participant.user_id for participant in participants])

    async def test_winner_when_called_then_result_saved(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        participants = self._create_participants(10)
        ctx.scrim.teams_manager.all_participants = participants
        team_1 = MagicMock()
        team_2 = MagicMock()
        await self.cog.winner(ctx, [(team_1, team_2)])
        self.result_handler.save_result.assert_called_with(ctx, [(team_1, team_2)])

    async def test_tie_when_called_then_behaviour_identical_to_winner_with_single_tuple_argument(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        team_1 = MagicMock()
        team_2 = MagicMock()
        mock_scrim.teams_manager = MagicMock()
        ctx.scrim.teams_manager.get_game_teams.return_value = [team_1, team_2]
        participants = self._create_participants(10)
        ctx.scrim.teams_manager.all_participants = participants
        await self.cog.tie(ctx)
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([(team_1, team_2)])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        self.active_scrims_manager.drop.assert_called_with(mock_scrim)
        self.participant_provider.drop_participants.assert_called_with(
            *[participant.user_id for participant in participants])

    async def test_end_when_called_then_behaviour_identical_to_winner_with_empty_list_argument(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        participants = self._create_participants(10)
        ctx.scrim.teams_manager.all_participants = participants
        await self.cog.end(ctx)
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        self.active_scrims_manager.drop.assert_called_with(mock_scrim)
        self.participant_provider.drop_participants.assert_called_with(
            *[participant.user_id for participant in participants])

    async def test_terminate_when_called_then_scrim_manager_terminate_called_and_message_deleted(self):
        mock_scrim = MagicMock()
        mock_scrim.state = ScrimState.STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        participants = self._create_participants(10)
        ctx.scrim.teams_manager.all_participants = participants
        await self.cog.terminate(ctx)
        ctx.message.delete.assert_called()
        mock_scrim.terminate.assert_called_with(ctx.author)
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        self.active_scrims_manager.drop.assert_called_with(mock_scrim)
        mock_scrim.message.clear_reactions.assert_called()
        self.participant_provider.drop_participants.assert_called_with(
            *[participant.user_id for participant in participants])

    async def test_teams_when_called_then_strategy_create_teams_called_embed_edited_and_message_deleted(self):
        self.mock_scrim.state = ScrimState.LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        mock_message = AsyncMock()
        ctx.channel.get_message.return_value = mock_message
        mock_strategy = AsyncMock()
        await self.cog.teams(ctx, mock_strategy)
        ctx.message.delete.assert_called()
        mock_strategy.create_teams.assert_called_with(self.mock_scrim, mock_message)
        self.response_builder.edit.assert_called_with(mock_message, displayable=self.mock_scrim)
        ctx.scrim.message.clear_reactions.assert_not_called()

    def _create_participants(self, amount: int) -> list[User]:
        participants = []
        for _ in range(amount):
            mock_participant = MagicMock()
            mock_participant.user_id = self.id_generator.generate_viable_id()
            participants.append(mock_participant)
        return participants
