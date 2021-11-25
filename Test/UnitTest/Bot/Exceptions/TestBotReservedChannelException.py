__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock

from Bot.Exceptions.BotReservedChannelException import BotReservedChannelException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotReservedChannelException(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def test_init_given_text_channel_tells_channel_reserved_for_scrim_already(self):
        embed_builder = AsyncMock()
        channel_id = self.id_generator.generate_viable_id()
        exception = BotReservedChannelException(channel_id, embed_builder)
        self.assertEqual(f"Text channel <#{channel_id}> is already registered for scrim usage.", exception.message)

    def test_init_given_voice_and_text_channel_tells_channel_reserved_for_scrim_elsewhere(self):
        embed_builder = AsyncMock()
        voice_channel_id, text_channel_id = self.id_generator.generate_viable_id_group(2)
        exception = BotReservedChannelException(voice_channel_id, embed_builder, text_channel_id)
        self.assertEqual(f"Voice channel <#{voice_channel_id}> is already associated with scrim "
                         f"channel <#{text_channel_id}>.", exception.message)

    async def test_resolve_given_called_then_embed_sent_with_message_and_help(self):
        prefix, command = "/", "test"
        mock_context = AsyncMock()
        mock_context.prefix = prefix
        mock_context.command.name = command
        mock_embed_builder = AsyncMock()
        new_exception = BotReservedChannelException(1, mock_embed_builder)
        await new_exception.resolve(mock_context)
        mock_embed_builder.send.assert_called_with(mock_context, displayable=new_exception)

