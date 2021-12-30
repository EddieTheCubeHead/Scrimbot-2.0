__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Checks.ActiveScrimCheck import ActiveScrimCheck
from Bot.Exceptions.BotMissingScrimException import BotMissingScrimException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestFreeScrimCheck(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.check = ActiveScrimCheck()
        self.context = AsyncMock()
        self.mock_converter = MagicMock()

    async def test_check_given_scrim_exists_then_returns_true(self):
        self.context.scrim = MagicMock()
        self.assertTrue(await self.check.check(self.context))

    async def test_check_given_no_scrim_then_error_raised(self):
        self.context.scrim = None
        channel_id = self.id_generator.generate_viable_id()
        self.context.channel.id = channel_id
        expected_exception = BotMissingScrimException(channel_id)
        await self._async_assert_raises_correct_exception(expected_exception, self.check.check, self.context)
