__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.VoiceChannel import VoiceChannel
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Bot.Exceptions.BotReservedChannelException import BotReservedChannelException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter


class TestScrimChannelConverter(AsyncUnittestBase):

    GUILD_ID = 1

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_database_connection = MagicMock()
        self.converter = ScrimChannelConverter(self.mock_database_connection)
        self.mock_database_connection.exists_text = MagicMock(return_value=None)
        self.mock_database_connection.exists_voice = MagicMock(return_value=None)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimChannelConverter)

    async def test_convert_given_valid_id_then_channel_returned(self):
        mock_id = self.id_generator.generate_viable_id()
        mock_method = MagicMock()
        self.mock_database_connection.get_channel = mock_method
        expected = ScrimChannel(mock_id, self.GUILD_ID)
        mock_method.return_value = expected
        actual = await self.converter.convert(MagicMock(), str(mock_id))
        self._assert_identical_data(actual, expected)

    async def test_convert_given_called_twice_then_cache_utilized(self):
        mock_id = self.id_generator.generate_viable_id()
        mock_method = MagicMock()
        self.mock_database_connection.get_channel = mock_method
        expected = ScrimChannel(mock_id, self.GUILD_ID)
        mock_method.return_value = expected
        await self.converter.convert(MagicMock(), str(mock_id))
        await self.converter.convert(MagicMock(), str(mock_id))
        self.mock_database_connection.get_channel.assert_called_once_with(mock_id)

    def test_add_given_new_channel_id_with_no_voice_channels_then_channel_added(self):
        channel_id, guild_id = self.id_generator.generate_viable_id_group(2)
        self.converter.add(channel_id, guild_id)
        self._assert_channel_added(channel_id, guild_id)

    def test_add_given_new_channel_id_with_voice_channels_and_lobby_then_channel_added(self):
        channel_id, guild_id = self.id_generator.generate_viable_id_group(2)
        for i in range(1, 6):
            with self.subTest(f"Adding scrim text channel with voice channels and lobby ({i} channels)"):
                voice_channels = self._generate_mock_voice_channels(channel_id, i, 0)
                self.converter.add(channel_id, guild_id, *voice_channels)
                self._assert_channel_added(channel_id, guild_id, *voice_channels)

    def test_add_given_new_channel_id_with_voice_channels_and_no_lobby_then_channel_added(self):
        channel_id, guild_id = self.id_generator.generate_viable_id_group(2)
        for i in range(2, 6):
            with self.subTest(f"Adding scrim text channel with voice channels and no lobby ({i} channels)"):
                voice_channels = self._generate_mock_voice_channels(channel_id, i, 1)
                self.converter.add(channel_id, guild_id, *voice_channels)
                self._assert_channel_added(channel_id, guild_id, *voice_channels)

    def test_add_given_already_registered_text_channel_then_exception_raised(self):
        channel_id, guild_id = self.id_generator.generate_viable_id_group(2)
        self.mock_database_connection.exists_text = MagicMock(return_value=ScrimChannel(channel_id, guild_id))
        expected_exception = BotReservedChannelException(channel_id)
        self._assert_raises_correct_exception(expected_exception, self.converter.add, channel_id, guild_id)

    def test_add_given_already_used_voice_channel_then_exception_raised(self):
        channel_id, guild_id = self.id_generator.generate_viable_id_group(2)
        reserved_id = self.id_generator.generate_nonviable_id()
        voice_channels = self._generate_mock_voice_channels(channel_id, 1, 1)
        taken_voice = VoiceChannel(voice_channels[0].channel_id, reserved_id, 2)
        self.mock_database_connection.exists_voice = MagicMock(return_value=taken_voice)
        expected_exception = BotReservedChannelException(taken_voice.channel_id, parent_channel_id=reserved_id)
        self._assert_raises_correct_exception(expected_exception, self.converter.add, channel_id, guild_id,
                                              *voice_channels)

    def _assert_identical_data(self, actual: ScrimChannel, expected: ScrimChannel):
        self.assertEqual(expected.channel_id, actual.channel_id)
        self.assertEqual(len(expected.voice_channels), len(actual.voice_channels))
        for index, channel in enumerate(expected.voice_channels):
            self.assertEqual(channel, expected.voice_channels[index])

    def _assert_channel_added(self, channel_id, guild_id, *voice_channels):
        actual_channel = self.mock_database_connection.add_channel.call_args[0][0]
        self.assertEqual(actual_channel.channel_id, channel_id)
        self.assertEqual(actual_channel.guild_id, guild_id)
        self.assertEqual(len(actual_channel.voice_channels), len(voice_channels))
        for channel in voice_channels:
            self.assertIn(channel, actual_channel.voice_channels)

    def _generate_mock_voice_channels(self, parent_id, amount, start_team):
        voice_channels = []
        for team in range(start_team, amount + start_team):
            voice_channels.append(VoiceChannel(self.id_generator.generate_viable_id(), parent_id, team))
        return voice_channels
