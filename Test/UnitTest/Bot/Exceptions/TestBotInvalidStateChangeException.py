__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestBotInvalidStateChangeException(AsyncUnittestBase):

    def test_init_given_two_states_then_message_set_from_state_descriptions(self):
        original_state = MagicMock()
        original_state.description = "original"
        new_state = MagicMock()
        new_state.description = "new"
        new_exception = BotInvalidStateChangeException(original_state, new_state, MagicMock())
        expected_message = "Could not move a scrim that is original into the state 'new'."
        self.assertEqual(expected_message, new_exception.message)

    async def test_resolve_when_called_then_deletion_time_set_to_60_seconds(self):
        original_state = MagicMock()
        original_state.description = "original"
        new_state = MagicMock()
        new_state.description = "new"
        mock_embed_builder = AsyncMock()
        new_exception = BotInvalidStateChangeException(original_state, new_state, mock_embed_builder)
        mock_context = AsyncMock()
        await new_exception.resolve(mock_context)
        mock_embed_builder.send.assert_called_with(mock_context, displayable=new_exception, delete_after=60)
