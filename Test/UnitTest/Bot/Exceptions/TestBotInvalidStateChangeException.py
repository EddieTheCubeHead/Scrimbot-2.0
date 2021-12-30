__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Utils.TestBases.UnittestBase import UnittestBase


class TestBotInvalidStateChangeException(UnittestBase):

    def test_init_given_two_states_then_message_set_from_state_descriptions(self):
        original_state = MagicMock()
        original_state.description = "original"
        new_state = MagicMock()
        new_state.description = "new"
        new_exception = BotInvalidStateChangeException(original_state, new_state)
        expected_message = "Could not move a scrim that is original into the state 'new'."
        self.assertEqual(expected_message, new_exception.message)
