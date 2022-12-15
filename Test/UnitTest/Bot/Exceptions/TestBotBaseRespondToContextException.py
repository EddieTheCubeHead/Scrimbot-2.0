__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class TestBotBaseRespondToContextException(AsyncUnittestBase):

    def test_get_help_portion_given_valid_context_then_correct_help_returned(self):
        prefix, command = "/", "test"
        mock_context = MagicMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        expected_help = f"{prefix}help {command}"
        new_exception = BotBaseRespondToContextException("Foo")
        self.assertEqual(expected_help, new_exception.get_help_portion(mock_context))

    async def test_resolve_given_only_message_then_embed_sent_with_message_and_help(self):
        prefix, command = "/", "test"
        mock_context = AsyncMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        mock_embed_builder = AsyncMock()
        new_exception = BotBaseRespondToContextException("Foo", mock_embed_builder)
        await new_exception.resolve(mock_context)
        mock_embed_builder.send.assert_called_with(mock_context, displayable=new_exception, delete_after=None)

    async def test_resolve_given_deletion_time_then_embed_sent_with_message_and_help_and_deletion_time_set(self):
        prefix, command = "/", "test"
        mock_context = AsyncMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        mock_embed_builder = AsyncMock()
        new_exception = BotBaseRespondToContextException("Foo", mock_embed_builder, delete_after=60)
        await new_exception.resolve(mock_context)
        mock_embed_builder.send.assert_called_with(mock_context, displayable=new_exception, delete_after=60)
