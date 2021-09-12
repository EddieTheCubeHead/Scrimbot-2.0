__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch, AsyncMock

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder
from Utils.test_utils import create_mock_context


class TestResponseBuilder(AsyncUnittestBase):

    def setUp(self) -> None:
        self.builder = ResponseBuilder()
        self.ctx = create_mock_context(1, 1, 1, ":ping")
        self.ctx.message = AsyncMock()

    def test_class_given_builder_exists_then_instance_dependency_created(self):
        self.assertIsNotNone(BotDependencyInjector.dependencies[ResponseBuilder])

    async def test_send_given_text_and_no_embed_builder_then_text_response_sent(self):
        _response = "Pong!"
        await self.builder.send(self.ctx, _response)
        self.ctx.send.assert_called_with(_response, delete_after=None)

    async def test_send_given_called_with_default_args_then_original_message_deleted(self):
        _response = "Pong!"
        await self.builder.send(self.ctx, _response)
        self.ctx.message.delete.assert_called_once()

    async def test_send_given_called_with_delete_false_arg_then_original_message_not_deleted(self):
        _response = "Pong!"
        await self.builder.send(self.ctx, _response, delete_parent=False)
        self.ctx.message.delete.assert_not_called()

    async def test_send_given_text_timeout_and_no_embed_builder_then_temporary_text_response_sent(self):
        _response = "Pong!"
        deletion_timeout = 15.5
        await self.builder.send(self.ctx, _response, delete_after=deletion_timeout)
        self.ctx.send.assert_called_with(_response, delete_after=deletion_timeout)

    async def test_send_given_embed_data_and_no_text_then_only_embed_response_sent(self):
        _embed = MagicMock()
        _embed_build = MagicMock(return_value=_embed)
        with patch("Bot.EmbedSystem.ResponseBuilder.ResponseBuilder.build", _embed_build):
            await self.builder.send(self.ctx, displayable=MagicMock())
        self.ctx.send.assert_called_with(None, embed=_embed, delete_after=None)

    async def test_send_given_embed_data_and_text_then_text_and_embed_response_sent(self):
        _response = "Pong!"
        _embed = MagicMock()
        _embed_build = MagicMock(return_value=_embed)
        with patch("Bot.EmbedSystem.ResponseBuilder.ResponseBuilder.build", _embed_build):
            await self.builder.send(self.ctx, _response, displayable=MagicMock())
        self.ctx.send.assert_called_with(_response, embed=_embed, delete_after=None)

    async def test_send_given_embed_data_text_and_deletion_time_then_temporary_text_and_embed_response_sent(self):
        deletion_timeout = 15.5
        _response = "Pong!"
        _embed = MagicMock()
        _embed_build = MagicMock(return_value=_embed)
        with patch("Bot.EmbedSystem.ResponseBuilder.ResponseBuilder.build", _embed_build):
            await self.builder.send(self.ctx, _response, displayable=MagicMock(), delete_after=deletion_timeout)
        self.ctx.send.assert_called_with(_response, embed=_embed, delete_after=deletion_timeout)
