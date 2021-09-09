__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, patch

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder
from Utils.test_utils import create_mock_context


class TestResponseBuilder(AsyncUnittestBase):

    def setUp(self) -> None:
        self.builder = ResponseBuilder()

    def test_class_given_builder_exists_then_instance_dependency_created(self):
        self.assertIsNotNone(BotDependencyInjector.dependencies[ResponseBuilder])

    async def test_send_given_text_and_no_embed_builder_then_text_response_sent(self):
        ctx = create_mock_context(1, 1, 1, ":ping")
        _response = "Pong!"
        await self.builder.send(ctx, _response)
        ctx.send.assert_called_with(_response, delete_after=None)

    async def test_send_given_text_timeout_and_no_embed_builder_then_temporary_text_response_sent(self):
        ctx = create_mock_context(1, 1, 1, ":ping")
        _response = "Pong!"
        deletion_timeout = 15.5
        await self.builder.send(ctx, _response, delete_after=deletion_timeout)
        ctx.send.assert_called_with(_response, delete_after=deletion_timeout)

    async def test_send_given_embed_data_and_no_text_then_only_embed_response_sent(self):
        ctx = create_mock_context(1, 1, 1, ":ping")
        _embed = MagicMock()
        _embed_build = MagicMock(return_value=_embed)
        with patch("Bot.EmbedSystem.ResponseBuilder.ResponseBuilder.build", _embed_build):
            await self.builder.send(ctx, displayable=MagicMock())
        ctx.send.assert_called_with(None, embed=_embed, delete_after=None)

    async def test_send_given_embed_data_and_text_then_text_and_embed_response_sent(self):
        ctx = create_mock_context(1, 1, 1, ":ping")
        _response = "Pong!"
        _embed = MagicMock()
        _embed_build = MagicMock(return_value=_embed)
        with patch("Bot.EmbedSystem.ResponseBuilder.ResponseBuilder.build", _embed_build):
            await self.builder.send(ctx, _response, displayable=MagicMock())
        ctx.send.assert_called_with(_response, embed=_embed, delete_after=None)

    async def test_send_given_embed_data_text_and_deletion_time_then_temporary_text_and_embed_response_sent(self):
        ctx = create_mock_context(1, 1, 1, ":ping")
        deletion_timeout = 15.5
        _response = "Pong!"
        _embed = MagicMock()
        _embed_build = MagicMock(return_value=_embed)
        with patch("Bot.EmbedSystem.ResponseBuilder.ResponseBuilder.build", _embed_build):
            await self.builder.send(ctx, _response, displayable=MagicMock(), delete_after=deletion_timeout)
        ctx.send.assert_called_with(_response, embed=_embed, delete_after=deletion_timeout)
