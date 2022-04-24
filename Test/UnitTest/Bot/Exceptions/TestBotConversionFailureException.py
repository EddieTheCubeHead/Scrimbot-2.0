__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Test.Utils.TestBases.UnittestBase import UnittestBase
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException


class TestBotConversionFailureException(UnittestBase):

    def test_init_given_valid_exception_then_correct_message_constructed(self):
        argument = "Foo"
        conversion_type = "Scrim"
        new_exception = BotConversionFailureException(conversion_type, "Foo")
        self.assertEqual(f"Could not convert argument '{argument}' into type {conversion_type}",
                         new_exception.message)
