__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from Bot.Cogs.ScrimCommands import ScrimCommands
from Bot.DataClasses.Game import Game
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimCommands(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.scrim_channel_converter = MagicMock()
        self.response_builder = AsyncMock()
        self.settings_service = MagicMock()
        self.active_scrims_manager = MagicMock()
        self.cog = ScrimCommands(self.scrim_channel_converter, self.response_builder, self.settings_service,
                                 self.active_scrims_manager)
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
