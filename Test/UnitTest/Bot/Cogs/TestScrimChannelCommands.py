__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Cogs.ScrimChannelCommands import ScrimChannelCommands
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.test_utils import create_mock_context


class TestScrimChannelCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.response_builder = AsyncMock()
        self.conversion_result = None
        self.mock_text_converter = MagicMock()
        self.mock_voice_manager = MagicMock()
        self.cog = ScrimChannelCommands(self.response_builder, self.mock_text_converter, self.mock_voice_manager)
        self.cog._inject(MagicMock())

    async def test_register_given_no_voice_channels_then_channel_registered_and_response_built_by_dependencies(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        await self.cog.register(ctx, [])
        self.response_builder.send.assert_called_with(ctx, displayable=result_channel)

    async def test_register_given_voice_channels_then_teams_enumerated(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        voice_channels = [VoiceChannel(1, 2)]
        await self.cog.register(ctx, voice_channels)
        self.mock_voice_manager.enumerate_teams.assert_called_with(voice_channels)
        self.response_builder.send.assert_called_with(ctx, displayable=result_channel)
