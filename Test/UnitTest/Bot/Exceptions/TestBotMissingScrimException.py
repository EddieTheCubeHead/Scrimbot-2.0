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

    def test_get_help_portion_given_valid_exception_then_correct_help_returned(self):
        channel_name = "foo"
        prefix = "/"
        mock_context = _create_mock_context(channel_name, prefix)
        mock_context.command.name = "register"
        expected_help = f"{prefix}help register"
        new_exception = BotMissingScrimException(mock_context)
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))
