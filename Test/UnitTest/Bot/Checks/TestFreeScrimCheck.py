__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from Src.Bot.Checks.FreeScrimCheck import FreeScrimCheck
from Src.Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Src.Bot.Exceptions.BotReservedChannelException import BotReservedChannelException
from Src.Bot.Exceptions.BotUnregisteredChannelException import BotUnregisteredChannelException
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestFreeScrimCheck(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.check = FreeScrimCheck()
        self.context = AsyncMock()
        self.mock_channel_converter = MagicMock()
        self.mock_scrim_converter = MagicMock()
        self.mock_scrim_converter.exists.return_value = False

    async def test_check_when_called_with_registered_channel_and_no_active_scrim_then_true_returned(self):
        self.context.channel = AsyncMock()
        self.context.channel.id = self.id_generator.generate_viable_id()
        self.mock_channel_converter.get_from_id.return_value = self.context.channel
        self.context.scrim = None
        self.assertTrue(await self.check.check(self.context, self.mock_channel_converter, self.mock_scrim_converter))

    async def test_check_when_called_with_unregistered_channel_then_unregistered_channel_exception_raised(self):
        self.context.channel = MagicMock()
        self.context.channel.id = self.id_generator.generate_viable_id()
        self.mock_channel_converter.get_from_id.side_effect = NoResultFound()
        self.context.scrim = None
        expected_exception = BotUnregisteredChannelException(self.context.channel.id)
        await self._async_assert_raises_correct_exception(expected_exception, self.check.check, self.context,
                                                          self.mock_channel_converter, self.mock_scrim_converter)

    async def test_check_when_called_with_channel_with_an_active_scrim_then_channel_has_scrim_exception_raised(self):
        self.context.channel = MagicMock()
        self.context.channel.id = self.id_generator.generate_viable_id()
        self.mock_scrim_converter.exists.return_value = True
        self.mock_channel_converter.get_from_id.return_value = self.context.channel
        expected_exception = BotChannelHasScrimException(self.context.channel.id)
        await self._async_assert_raises_correct_exception(expected_exception, self.check.check, self.context,
                                                          self.mock_channel_converter, self.mock_scrim_converter)
