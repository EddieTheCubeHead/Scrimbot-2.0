__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Exceptions.BuildException import BuildException
from Bot.Logic.DiscordObjectProvider import DiscordObjectProvider
from Utils.TestBases.UnittestBase import UnittestBase


class TestDiscordObjectProvider(UnittestBase):

    def setUp(self) -> None:
        self.provider = DiscordObjectProvider()

    def test_set_client_when_given_client_then_registered_correctly(self):
        mock_client = MagicMock()
        self.provider.client = mock_client
        self.assertEqual(mock_client, self.provider.client)

    def test_set_client_given_client_already_set_when_given_client_then_error_raised(self):
        self.provider.client = MagicMock()
        mock_exception = BuildException("Tried to set client for Discord voice channel provider while client was "
                                        "already set.")

        def assignment(provider, client):
            provider.client = client

        self._assert_raises_correct_exception(mock_exception, assignment, self.provider, MagicMock())
