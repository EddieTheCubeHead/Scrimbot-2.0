__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import patch, AsyncMock, MagicMock

from Bot.DataClasses.VoiceChannel import VoiceChannel
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Bot.Converters.VoiceChannelConverter import VoiceChannelConverter


class TestVoiceChannelConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.discord_convert = AsyncMock()
        self.connection = MagicMock()
        self.converter = VoiceChannelConverter(self.connection)

    async def test_convert_given_existing_channel_id_then_discord_convert_called_and_channel_returned(self):
        channel_id, parent_id = self.id_mocker.generate_viable_id_group(2)
        mock_discord_channel = MagicMock()
        mock_discord_channel.id = channel_id
        self.discord_convert.return_value = mock_discord_channel
        mock_context = MagicMock()
        mock_context.channel.id = parent_id
        with patch("discord.ext.commands.converter.VoiceChannelConverter.convert", self.discord_convert):
            actual = await self.converter.convert(mock_context, str(channel_id))
        expected = VoiceChannel(channel_id, parent_id)
        self._assert_correct_channel_data(expected, actual)

    async def test_convert_given_channel_id_preceded_by_lobby_tag_then_lobby_channel_returned(self):
        channel_id, parent_id = self.id_mocker.generate_viable_id_group(2)
        mock_discord_channel = MagicMock()
        mock_discord_channel.id = channel_id
        self.discord_convert.return_value = mock_discord_channel
        mock_context = MagicMock()
        mock_context.channel.id = parent_id
        with patch("discord.ext.commands.converter.VoiceChannelConverter.convert", self.discord_convert):
            actual = await self.converter.convert(mock_context, f"l:{channel_id}")
        expected = VoiceChannel(channel_id, parent_id, 0)
        self._assert_correct_channel_data(expected, actual)

    def _assert_correct_channel_data(self, expected: VoiceChannel, actual: VoiceChannel):
        self.assertEqual(expected.channel_id, actual.channel_id)
        self.assertEqual(expected.parent_channel_id, actual.parent_channel_id)
        self.assertEqual(expected.team, actual.team)
