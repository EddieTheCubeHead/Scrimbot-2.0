__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.TestBases.UnittestBase import UnittestBase
from Bot.Exceptions.BotMissingScrimException import BotMissingScrimException


def _create_mock_context(channel_name, prefix="/"):
    mock_context = MagicMock()
    mock_context.channel.name = channel_name
    mock_context.prefix = prefix
    return mock_context


class TestDatabaseBaseException(UnittestBase):

    def test_get_description_given_valid_exception_then_correct_description_returned(self):
        channel_name = "test-channel"
        mock_context = _create_mock_context(channel_name)
        expected_description = f"Seems like the channel '{channel_name}' is not registered for scrim usage."
        new_exception = BotMissingScrimException(mock_context)
        self.assertEqual(expected_description, new_exception.get_description())

    def test_get_help_portion_given_valid_exception_then_correct_help_returned(self):
        channel_name = "foo"
        prefix = "/"
        mock_context = _create_mock_context(channel_name, prefix)
        expected_help = f"\n\nTo get help with registering channels, use the command '{prefix}help register'"
        new_exception = BotMissingScrimException(mock_context)
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))

    def test_get_help_portion_given_exception_with_send_help_disabled_then_empty_string_returned(self):
        channel_name = "foo"
        prefix = "/"
        mock_context = _create_mock_context(channel_name, prefix)
        expected_help = ""
        new_exception = BotMissingScrimException(mock_context, send_help=False)
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))
