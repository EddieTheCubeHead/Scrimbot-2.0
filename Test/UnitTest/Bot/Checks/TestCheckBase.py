__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch

from discord import Intents
from discord.ext.commands import Context, Bot

from Bot.Checks.CheckBase import CheckBase
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.test_utils import create_mock_guild, create_mock_channel, create_mock_author, \
    create_async_mock_message


class TestCheck(CheckBase):

    check_call_counter = 0

    @classmethod
    def check(cls, ctx: Context):
        cls.check_call_counter += 1
        return True


class TestBot(Bot):
    pass


bot = TestBot(command_prefix='?', description="Test bot", intents=Intents.default())


@bot.command(name="test")
@TestCheck.decorate()
async def test_func(ctx):
    pass


class TestCheckBase(AsyncUnittestBase):

    async def test_decorator_functionality_when_decorated_with_class_class_check_returned(self):
        mock_guild = create_mock_guild(1)
        mock_channel = create_mock_channel(1, mock_guild)
        mock_author = create_mock_author(1, mock_guild)
        test_message = create_async_mock_message(mock_guild, mock_channel, mock_author, "?test")
        with patch("UnitTest.Bot.Checks.TestCheckBase.TestBot.user", MagicMock()):
            await bot.on_message(test_message)
        self.assertEqual(1, TestCheck.check_call_counter)
