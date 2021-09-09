__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch, AsyncMock

from Bot.Cogs.ScrimChannelCommands import ScrimChannelCommands
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Utils.test_utils import create_mock_context


class TestScrimChannelCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.response_builder = AsyncMock()
        self.conversion_result = None
        self.mock_text_converter = MagicMock()
        self.cog = ScrimChannelCommands(self.response_builder, self.mock_text_converter)
        self.cog._inject(MagicMock())

    async def test_register_given_no_voice_channels_then_channel_registered_and_response_built_by_dependencies(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        await self.cog.register(ctx)
        self.response_builder.send.assert_called_with("New scrim channel registered successfully! Channel info:",
                                                      displayable=result_channel)

    async def test_register_given_one_voice_channel_then_channel_registered_and_response_built_by_dependencies(self):
        result_channel = AsyncMock()
        self.mock_text_converter.add = MagicMock(return_value=result_channel)
        ctx = create_mock_context(1, 1, 1, ":register")
        await self.cog.register(ctx)
        self.response_builder.send.assert_called_with("New scrim channel registered successfully! Channel info:",
                                                      displayable=result_channel)
