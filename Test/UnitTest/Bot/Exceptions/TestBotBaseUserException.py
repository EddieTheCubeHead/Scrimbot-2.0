__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestBases.UnittestBase import UnittestBase
from Bot.Exceptions.BotBaseUserException import BotBaseUserException


class TestBotBaseUserException(AsyncUnittestBase):

    def test_get_help_portion_given_valid_context_then_correct_help_returned(self):
        prefix, command = "/", "test"
        mock_context = MagicMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        expected_help = f"{prefix}help {command}"
        new_exception = BotBaseUserException("Foo")
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))

    async def test_resolve_given_only_message_then_embed_sent_with_message_and_help(self):
        prefix, command = "/", "test"
        mock_context = AsyncMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        mock_embed_builder = AsyncMock()
        new_exception = BotBaseUserException("Foo", mock_embed_builder)
        await new_exception.resolve(mock_context)
        mock_embed_builder.send.assert_called_with(mock_context, displayable=new_exception)
