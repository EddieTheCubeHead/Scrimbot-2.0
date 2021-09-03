__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter


class TestScrimChannelConverter(UnittestBase):

    GUILD_ID = 1

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_database_connection = MagicMock()
        self.converter = ScrimChannelConverter(self.mock_database_connection)

    def test_init_given_normal_init_then_converter_for_game_dataclass_set(self):
        self.assertIn(ScrimChannelConverter, BotDependencyConstructor.converters.values())

    def test_convert_given_valid_id_then_channel_returned(self):
        mock_id = self.id_generator.generate_viable_id()
        mock_method = MagicMock()
        self.mock_database_connection.get_channel = mock_method
        expected = ScrimChannel(mock_id, self.GUILD_ID)
        mock_method.return_value = expected
        actual = self.converter.convert(str(mock_id))
        self._assert_identical_data(actual, expected)

    def test_convert_given_called_twice_then_cache_utilized(self):
        mock_id = self.id_generator.generate_viable_id()
        mock_method = MagicMock()
        self.mock_database_connection.get_channel = mock_method
        expected = ScrimChannel(mock_id, self.GUILD_ID)
        mock_method.return_value = expected
        self.converter.convert(str(mock_id))
        self.converter.convert(str(mock_id))
        self.mock_database_connection.get_channel.assert_called_once_with(mock_id)

    def _assert_identical_data(self, actual: ScrimChannel, expected: ScrimChannel):
        self.assertEqual(expected.channel_id, actual.channel_id)
        self.assertEqual(len(expected.voice_channels), len(actual.voice_channels))
        for index, channel in enumerate(expected.voice_channels):
            self.assertEqual(channel, expected.voice_channels[index])
