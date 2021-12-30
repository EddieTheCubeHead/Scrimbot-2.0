__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.TestBases.UnittestBase import UnittestBase
from Bot.Exceptions.BotMissingScrimException import BotMissingScrimException
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestDatabaseBaseException(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def test_init_given_exception_build_then_correct_error_message_assigned(self):
        channel_id = self.id_mocker.generate_viable_id()
        expected_message = f"Could not find a scrim from channel <#{channel_id}>."
        new_exception = BotMissingScrimException(channel_id)
        self.assertEqual(expected_message, new_exception.message)
