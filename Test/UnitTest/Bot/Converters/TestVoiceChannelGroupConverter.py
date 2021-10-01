__version__ = "ver"
__author__ = "Eetu Asikainen"

import itertools
import os
from unittest.mock import MagicMock

import discord

from Bot.DataClasses.VoiceChannel import VoiceChannel
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Bot.Converters.VoiceChannelGroupConverter import VoiceChannelGroupConverter, DO_CONVERSION_STRINGS
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _get_expected_team(pattern, expected_channel):
    first_digit_index = 0


class TestVoiceChannelGroupConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.converter = VoiceChannelGroupConverter(self.connection)

    async def test_convert_given_valid_string_then_channels_fetched_from_category_and_teams_set_from_name(self):
        mock_context = MagicMock()
        channel_names = "Team 1", "Team 2", "Team 3"
        name_pattern = "Team ?"
        mock_channel_list = self._create_mock_channel_group(*channel_names)
        mock_context.channel.category.voice_channels = mock_channel_list
        for string in DO_CONVERSION_STRINGS:
            with self.subTest(f"Convert voice channels from group automatically with argument {string}"):
                actual_channels = await self.converter.convert(mock_context, string)
                self._assert_channels_converted(name_pattern, mock_channel_list, actual_channels)

    async def test_convert_given_ctx_with_channel_with_no_category_then_exception_raised(self):
        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.channel.name = "scrim-channel"
        mock_context.channel.category = None
        expected_exception = BotBaseUserException("Cannot automatically assign voice channels from category because "
                                                  f"channel '{mock_context.channel.name}' doesn't belong in a category")
        await self._async_assert_raises_correct_exception(expected_exception, self.converter.convert, mock_context,
                                                          DO_CONVERSION_STRINGS[0])

    def _create_mock_channel_group(self, *channel_names: str):
        voice_channels = []
        for name in channel_names:
            mock_channel = MagicMock()
            mock_channel.name = name
            mock_channel.id = self.id_mocker.generate_viable_id()
            voice_channels.append(mock_channel)
        return voice_channels

    def _assert_channels_converted(self, name_pattern: str, expected_channels: list[discord.VoiceChannel],
                                   actual_channels: list[VoiceChannel]):
        self.assertEqual(len(expected_channels), len(actual_channels))
        for expected_channel, actual_channel in zip(expected_channels, actual_channels):
            self.assertEqual(expected_channel.id, actual_channel.id)
            self._assert_correct_team(name_pattern, expected_channel, actual_channel)

    def _assert_correct_team(self, pattern, expected_channel, actual_channel):
        expected_team = _get_expected_team(pattern, expected_channel)
        self.assertEqual(expected_team, actual_channel.team)
