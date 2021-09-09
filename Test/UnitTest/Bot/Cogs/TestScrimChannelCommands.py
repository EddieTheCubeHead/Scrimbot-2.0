__version__ = "ver"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from Bot.Cogs.ScrimChannelCommands import ScrimChannelCommands
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Utils.test_utils import create_mock_context


class TestScrimChannelCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.client = MagicMock()
        self.response_builder = MagicMock()
        self.Cog = ScrimChannelCommands(self.client, self.response_builder)

    async def test_register_given_one_channel_as_argument_then_channel_registered_with_no_voice_channels(self):
        ctx = create_mock_context(1, 1, 1, ":register 1")
        await self.Cog.register(ctx, ctx.message)

