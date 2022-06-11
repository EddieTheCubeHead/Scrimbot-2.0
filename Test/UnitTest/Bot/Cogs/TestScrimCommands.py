__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock, call

from Bot.Cogs.ScrimCommands import ScrimCommands
from Bot.DataClasses.Game import Game
from Bot.EmbedSystem.ScrimStates.scrim_states import *
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
        self.active_scrims_manager = MagicMock()
        self.waiting_scrim_service = MagicMock()
        self.cog = ScrimCommands(self.scrim_channel_converter, self.response_builder, self.settings_service,
                                 self.active_scrims_manager, self.waiting_scrim_service)
        self.cog._inject(MagicMock())

    async def test_scrim_given_called_with_game_then_scrim_with_game_created_and_embed_sent(self):
        game = Game("Test", "0xffffff", "icon_url", 5)
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = None
        result_scrim = MagicMock()
        mock_scrim_channel = MagicMock()
        self.scrim_channel_converter.get_from_id.return_value = mock_scrim_channel
        self.active_scrims_manager.create_scrim.return_value = result_scrim
        await self.cog.scrim(ctx, game)
        self.scrim_channel_converter.get_from_id.assert_called_with(ctx.channel.id)
        self.active_scrims_manager.create_scrim.assert_called_with(mock_scrim_channel, game)
        self.response_builder.send.assert_called_with(ctx, displayable=result_scrim)

    async def test_scrim_given_called_with_game_then_team_joining_reactions_added(self):
        game = Game("Test", "0xffffff", "icon_url", 5)
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = None
        result_scrim = MagicMock()
        mock_scrim_channel = MagicMock()
        scrim_message = AsyncMock()
        self.scrim_channel_converter.get_from_id.return_value = mock_scrim_channel
        self.active_scrims_manager.create_scrim.return_value = result_scrim
        self.response_builder.send.return_value = scrim_message
        await self.cog.scrim(ctx, game)
        calls = scrim_message.add_reaction.call_args_list
        self.assertEqual(calls[0], call(emoji="\U0001F3AE"))
        self.assertEqual(calls[1], call(emoji="\U0001F441"))

    async def test_scrim_given_called_successfully_then_message_saved_to_scrim_manager(self):
        game = Game("Test", "0xffffff", "icon_url", 5)
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = None
        result_scrim = MagicMock()
        mock_scrim_channel = MagicMock()
        scrim_message = AsyncMock()
        self.scrim_channel_converter.get_from_id.return_value = mock_scrim_channel
        self.active_scrims_manager.create_scrim.return_value = result_scrim
        self.response_builder.send.return_value = scrim_message
        await self.cog.scrim(ctx, game)
        self.assertEqual(scrim_message, result_scrim.message)

    async def test_lock_given_called_with_enough_participants_then_scrim_locked_and_message_edited(self):
        mock_scrim = MagicMock()
        mock_scrim.state = LFP
        mock_message = AsyncMock()
        mock_scrim.message = mock_message
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        await self.cog.lock(ctx)
        mock_scrim.lock.assert_called_with()
        self.response_builder.edit.assert_called_with(mock_message, displayable=mock_scrim)
        ctx.message.delete.assert_called()

    async def test_lock_given_locked_then_scrim_joining_reactions_removed_and_team_joining_reactions_added(self):
        mock_scrim = MagicMock()
        mock_scrim.state = LFP
        mock_message = AsyncMock()
        mock_scrim.message = mock_message
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        for team_count in range(2, 10):
            with self.subTest(f"Scrim locking reaction updates ({team_count} teams)"):
                mock_scrim.teams_manager.get_game_teams.return_value = ["Team"] * team_count
                await self.cog.lock(ctx)
                mock_message.clear_reactions.assert_called()
                calls = mock_message.add_reaction.call_args_list
                for team in range(team_count):
                    self.assertEqual(calls[team], call(emoji=f"{team + 1}\u20E3"))
                mock_message.add_reaction.call_args_list = []

    async def test_start_given_no_move_voice_arg_then_player_moving_attempted(self):
        mock_scrim = AsyncMock()
        mock_scrim.start = MagicMock()
        mock_scrim.state = LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        await self.cog.start(ctx)
        mock_scrim.start_with_voice.assert_called()
        ctx.message.delete.assert_called()
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        mock_scrim.message.clear_reactions.assert_called()

    async def test_start_when_player_moving_attended_successfully_then_scrim_not_registered_for_wait(self):
        mock_scrim = AsyncMock()
        mock_scrim.start = MagicMock()
        mock_scrim.state = LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        mock_scrim.message = AsyncMock()
        mock_scrim.start_with_voice.return_value = True
        await self.cog.start(ctx)
        self.waiting_scrim_service.register.assert_not_called()

    async def test_start_when_player_moving_attended_unsuccessfully_then_scrim_registered_for_wait(self):
        mock_scrim = AsyncMock()
        mock_scrim.start = MagicMock()
        mock_scrim.state = LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        mock_scrim.message = AsyncMock()
        mock_scrim.start_with_voice.return_value = False
        await self.cog.start(ctx)
        self.waiting_scrim_service.register.assert_called_with(mock_scrim)

    async def test_start_given_negative_move_voice_arg_then_started_without_moving(self):
        mock_scrim = AsyncMock()
        mock_scrim.start = MagicMock()
        mock_scrim.state = LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        await self.cog.start(ctx, False)
        mock_scrim.start.assert_called()
        ctx.message.delete.assert_called()
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        mock_scrim.message.clear_reactions.assert_called()

    async def test_start_given_not_enough_voice_channels_then_started_without_moving(self):
        mock_scrim = AsyncMock()
        mock_scrim.start = MagicMock()
        mock_scrim.state = LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        mock_scrim.teams_manager.supports_voice = False
        await self.cog.start(ctx)
        mock_scrim.start.assert_called()
        ctx.message.delete.assert_called()
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        mock_scrim.message.clear_reactions.assert_called()

    async def test_winner_given_team_name_then_team_made_winner(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = STARTED
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
        mock_scrim.state = STARTED
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
        mock_scrim.state = STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        await self.cog.winner(ctx, [])
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)

    async def test_tie_when_called_then_behaviour_identical_to_winner_with_single_tuple_argument(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        team_1 = MagicMock()
        team_2 = MagicMock()
        mock_scrim.teams_manager = MagicMock()
        ctx.scrim.teams_manager.get_game_teams.return_value = [team_1, team_2]
        await self.cog.tie(ctx)
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([(team_1, team_2)])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)

    async def test_end_when_called_then_behaviour_identical_to_winner_with_empty_list_argument(self):
        mock_scrim = AsyncMock()
        mock_scrim.state = STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        await self.cog.end(ctx)
        ctx.message.delete.assert_called()
        mock_scrim.end.assert_called_with([])
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)

    async def test_terminate_when_called_then_scrim_manager_terminate_called_and_message_deleted(self):
        mock_scrim = MagicMock()
        mock_scrim.state = STARTED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        await self.cog.terminate(ctx)
        ctx.message.delete.assert_called()
        mock_scrim.terminate.assert_called_with(ctx.author)
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        self.active_scrims_manager.drop.assert_called_with(mock_scrim)
        mock_scrim.message.clear_reactions.assert_called()

    async def test_teams_when_called_then_strategy_create_teams_called_embed_edited_and_message_deleted(self):
        mock_scrim = MagicMock()
        mock_scrim.state = LOCKED
        ctx = AsyncMock()
        ctx.channel.id = self.id_generator.generate_viable_id()
        ctx.scrim = mock_scrim
        ctx.scrim.message = AsyncMock()
        mock_strategy = AsyncMock()
        await self.cog.teams(ctx, mock_strategy)
        ctx.message.delete.assert_called()
        mock_strategy.create_teams.assert_called_with(mock_scrim)
        self.response_builder.edit.assert_called_with(ctx.scrim.message, displayable=mock_scrim)
        ctx.scrim.message.clear_reactions.assert_not_called()
