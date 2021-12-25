__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.Helpers.ChannelGroupParser import ChannelGroupParser
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Bot.Converters.VoiceChannelGroupConverter import VoiceChannelGroupConverter, DO_CONVERSION_STRINGS
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestVoiceChannelGroupConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.parser = ChannelGroupParser()
        self.converter = VoiceChannelGroupConverter(self.connection, self.parser)

    async def test_convert_given_ctx_with_channel_with_no_category_then_exception_raised(self):
        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.channel.name = "scrim-channel"
        mock_context.channel.category = None
        expected_exception = BotBaseUserException("Cannot automatically assign voice channels from category because "
                                                  f"channel '{mock_context.channel.name}' doesn't belong in a category")
        await self._async_assert_raises_correct_exception(expected_exception, self.converter.convert, mock_context,
                                                          DO_CONVERSION_STRINGS[0])

    async def test_convert_given_valid_channel_group_then_parser_called_and_teams_build_from_return_value(self):
        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.channel.name = "scrim-channel"
        mock_context.channel.category = self._create_mock_channel_group("1", "2", "0")
        actual_channels = await self.converter.convert(mock_context, DO_CONVERSION_STRINGS[0])
        self._assert_correct_channels(actual_channels, 0, 2)

    def _create_mock_channel_group(self, *channel_names: str):
        voice_channels = []
        for name in channel_names:
            mock_channel = MagicMock()
            mock_channel.name = name
            mock_channel.id = self.id_mocker.generate_viable_id()
            voice_channels.append(mock_channel)
        category = MagicMock()
        category.voice_channels = voice_channels
        parsed_channels = [(channel, int(channel.name)) for channel in voice_channels]
        parsed_channels.sort(key=lambda pair: pair[1])
        self.parser.parse = MagicMock(return_value=parsed_channels)
        return category

    def _assert_correct_channels(self, actual_channels, first_team, last_team):
        self.assertEqual(last_team - first_team + 1, len(actual_channels))
        for channel, expected_team in zip(actual_channels, range(first_team, last_team)):
            self.assertEqual(expected_team, channel.team)
