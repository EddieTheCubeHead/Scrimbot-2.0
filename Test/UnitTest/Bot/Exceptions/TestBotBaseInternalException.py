__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Utils.UnittestBase import UnittestBase
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class TestBotBaseUserException(UnittestBase):

    def test_get_message_given_valid_message_then_correct_message_received(self):
        test_msg = "Test error please ignore"
        new_exception = BotBaseInternalException(test_msg)
        self.assertEqual(test_msg, new_exception.get_message())

    def test_init_given_logging_not_specified_then_logging_enabled(self):
        new_exception = BotBaseInternalException("Foo")
        self.assertTrue(new_exception.log)

    def test_init_given_logging_disabled_then_value_set_correctly(self):
        new_exception = BotBaseInternalException("Foo", log=False)
        self.assertFalse(new_exception.log)
