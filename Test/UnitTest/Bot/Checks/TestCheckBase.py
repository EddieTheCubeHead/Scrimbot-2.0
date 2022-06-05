__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch

from discord import Intents
from discord.ext.commands import Context, Bot

from Bot.Checks.CheckBase import CheckBase
from Bot.Core.ScrimContext import ScrimContext
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.test_utils import create_mock_guild, create_mock_channel, create_mock_author, \
    create_async_mock_message


class TestCheck(CheckBase):

    check_call_counter = 0

    async def check(self, ctx: ScrimContext):
        self.__class__.check_call_counter += 1
        return True


class ArgsTestCheck(CheckBase):

    def __init__(self, increment_amount: int):
        self.increment_amount = increment_amount

    check_call_counter = 0

    async def check(self, ctx: ScrimContext):
        self.__class__.check_call_counter += self.increment_amount
        return True


class TestBot(Bot):
    pass


bot = TestBot(command_prefix='?', description="Test bot", intents=Intents.default())


@bot.command(name="test")
@TestCheck()
async def test_func(ctx):
    pass


@bot.command(name="args_test")
@ArgsTestCheck(5)
async def test_func(ctx):
    pass


class TestCheckBase(AsyncUnittestBase):

    async def test_decorator_given_function_decorated_then_class_class_check_returned(self):
        mock_guild = create_mock_guild(1)
        mock_channel = create_mock_channel(1, mock_guild)
        mock_author = create_mock_author(1, mock_guild)
        test_message = create_async_mock_message(mock_guild, mock_channel, mock_author, "?test")
        with patch("UnitTest.Bot.Checks.TestCheckBase.TestBot.user", MagicMock()):
            await bot.on_message(test_message)
        self.assertEqual(1, TestCheck.check_call_counter)

    async def test_decorator_given_args_then_args_usable_in_decorator(self):
        mock_guild = create_mock_guild(1)
        mock_channel = create_mock_channel(1, mock_guild)
        mock_author = create_mock_author(1, mock_guild)
        test_message = create_async_mock_message(mock_guild, mock_channel, mock_author, "?args_test")
        with patch("UnitTest.Bot.Checks.TestCheckBase.TestBot.user", MagicMock()):
            await bot.on_message(test_message)
        self.assertEqual(5, ArgsTestCheck.check_call_counter)


