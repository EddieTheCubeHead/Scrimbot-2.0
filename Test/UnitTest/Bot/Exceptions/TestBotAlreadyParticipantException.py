__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase

from Src.Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotAlreadyParticipantException(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def test_init_given_member_then_message_with_member_id_constructed(self):
        mock_id = self.id_generator.generate_viable_id()
        expected_message = f"Couldn't add user <@{mock_id}> to a team, because they are already participating in a " \
                           f"scrim."
        mock_member = MagicMock()
        mock_member.id = mock_id
        exception = BotAlreadyParticipantException(mock_member)
        self.assertEqual(expected_message, exception.message)

    async def test_resolve_when_called_then_message_logged_with_debug_level(self):
        mock_member = MagicMock()
        mock_team = MagicMock()
        mock_logger = MagicMock()
        await BotAlreadyParticipantException(mock_member, mock_logger).resolve()
        mock_logger.debug.assert_called()
