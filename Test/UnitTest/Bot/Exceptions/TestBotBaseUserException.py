__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.UnittestBase import UnittestBase
from Bot.Exceptions.BotBaseUserException import BotBaseUserException


class TestBotBaseUserException(UnittestBase):

    def test_get_header_given_valid_construction_then_correct_string_returned(self):
        new_exception = BotBaseUserException("Foo")
        self.assertEqual("Error: ", new_exception.get_header())

    def test_get_description_given_valid_message_then_correct_message_returned(self):
        test_message = "Test message please ignore"
        new_exception = BotBaseUserException(test_message)
        self.assertEqual(test_message, new_exception.get_description())

    def test_get_help_portion_given_valid_context_then_correct_help_returned(self):
        prefix, command = "/", "test"
        mock_context = MagicMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        expected_help = f"\n\nTo get help with this command, use the command '{prefix}help {command}'"
        new_exception = BotBaseUserException("Foo")
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))

    def test_get_help_portion_given_send_help_disabled_then_empty_string_returned(self):
        mock_context = MagicMock()
        expected_help = ""
        new_exception = BotBaseUserException("Foo", send_help=False)
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))
