__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Src.Bot.Cogs.ScrimChannelCommands import ScrimChannelCommands
from Src.Bot.DataClasses.VoiceChannel import VoiceChannel
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.test_utils import create_mock_context


class TestScrimChannelCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.response_builder = AsyncMock()
        self.mock_text_converter = MagicMock()
        self.mock_voice_manager = MagicMock()
        self.cog = ScrimChannelCommands(self.response_builder, self.mock_text_converter, self.mock_voice_manager)
        self.cog._inject(MagicMock())

    async def test_register_given_no_voice_channels_then_channel_registered_and_response_built_by_dependencies(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        await self.cog.register(ctx, [], None)
        self.response_builder.send.assert_called_with(ctx, displayable=result_channel)

    async def test_register_given_voice_channels_then_teams_enumerated(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        voice_channels = [VoiceChannel(2, 1), VoiceChannel(3, 1), VoiceChannel(4, 1)]
        await self.cog.register(ctx, voice_channels, None)
        self.mock_voice_manager.enumerate_teams.assert_called_with(voice_channels)
        self.response_builder.send.assert_called_with(ctx, displayable=result_channel)

    async def test_register_given_voice_channels_from_group_then_channels_treated_same_as_manual_channels(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        voice_channels = [VoiceChannel(2, 1), VoiceChannel(3, 1), VoiceChannel(4, 1)]
        await self.cog.register(ctx, [], voice_channels)
        self.mock_voice_manager.enumerate_teams.assert_called_with(voice_channels)
        self.response_builder.send.assert_called_with(ctx, displayable=result_channel)
