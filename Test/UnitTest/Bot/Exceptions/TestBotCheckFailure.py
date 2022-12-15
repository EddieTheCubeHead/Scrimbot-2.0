__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Test.Utils.TestBases.UnittestBase import UnittestBase
from Src.Bot.Exceptions.BotCheckFailure import BotCheckFailure


class TestBotCheckFailure(UnittestBase):

    def test_get_header_given_valid_exception_then_correct_string_returned(self):
        new_exception = BotCheckFailure("Foo")
        self.assertEqual("Check failed:", new_exception.get_header())
