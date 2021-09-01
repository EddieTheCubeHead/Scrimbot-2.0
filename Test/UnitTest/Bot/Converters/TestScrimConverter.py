__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter


class TestScrimConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_database_connection = MagicMock()
        self.converter = ScrimChannelConverter(self.mock_database_connection)

    def test_init_given_normal_init_then_converter_for_game_dataclass_set(self):
        self.assertIn(ScrimChannelConverter, BotDependencyConstructor.converters.values())

    def test_convert_given_id_not_in_active_scrims_when_id_is_valid_scrim_channel_then_scrim_created_and_saved(self):
        mock_id = self.id_generator.generate_viable_id()
        mock_method = MagicMock()
        self.mock_database_connection.get_from_id = mock_method
        mock_method.return_value
        # self.converter.convert(mock_id)
