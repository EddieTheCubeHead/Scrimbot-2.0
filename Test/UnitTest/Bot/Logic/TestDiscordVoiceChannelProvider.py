__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from Bot.Exceptions.BuildException import BuildException
from Bot.Logic.DiscordVoiceChannelProvider import DiscordVoiceChannelProvider
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestDiscordVoiceChannelProvider(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.provider = DiscordVoiceChannelProvider()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(DiscordVoiceChannelProvider)

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

    def test_get_channel_given_client_set_then_channel_fetched_from_client(self):
        mock_client = MagicMock()
        self.provider.client = mock_client
        mock_id = self.id_generator.generate_viable_id()
        self.provider.get_channel(mock_id)
        mock_client.get_channel.assert_called_with(mock_id)

    def test_channel_given_client_not_set_then_error_raised(self):
        mock_exception = BuildException("Tried to fetch a channel from channel provider but the provider client was "
                                        "not set. Please ensure bot initialization is working correctly.")
        self._assert_raises_correct_exception(mock_exception, self.provider.get_channel,
                                              self.id_generator.generate_viable_id())
