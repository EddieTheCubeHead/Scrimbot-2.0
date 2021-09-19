__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.exc import NoResultFound

from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Utils.TestBases.ConnectionUnittest import ConnectionUnittest
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


def _generate_voice_channels(voice_ids, parent_channel_id) -> list[VoiceChannel]:
    voice_channels: list[VoiceChannel] = []
    for team, voice_id in enumerate(voice_ids):
        voice_channels.append(VoiceChannel(voice_id, parent_channel_id, team))
    return voice_channels


class TestScrimChannelConnection(ConnectionUnittest[ScrimChannel]):

    _GUILD_ID = 1
    config: Config = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = Config()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection: ScrimChannelConnection = ScrimChannelConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimChannelConnection)

    def test_get_channel_given_valid_id_then_channel_returned_with_voice_channels(self):
        channel_id = self.id_generator.generate_viable_id()
        voice_ids = self.id_generator.generate_viable_id_group(4)
        self._insert_channel(channel_id, *voice_ids)
        actual = self.connection.get_channel(channel_id)
        self._assert_successful_fetch(actual)
        self._assert_has_voices(actual, voice_ids)

    def test_get_channel_when_no_channel_found_then_exception_raised(self):
        invalid_channel_id = self.id_generator.generate_nonviable_id()
        expected_exception = NoResultFound("No row was found when one was required")
        self._assert_raises_correct_exception(expected_exception, self.connection.get_channel, invalid_channel_id)

    def test_add_channel_given_valid_channel_then_channel_and_voices_successfully_added(self):
        channel_id = self.id_generator.generate_viable_id()
        voice_ids = self.id_generator.generate_viable_id_group(4)
        voice_channels: list[VoiceChannel] = _generate_voice_channels(voice_ids, channel_id)
        channel: ScrimChannel = ScrimChannel(channel_id, self._GUILD_ID, *voice_channels)
        self.connection.add_channel(channel)
        self._assert_channel_in_database(channel_id, voice_ids)

    def test_add_channel_given_valid_channel_then_channel_and_voices_returned(self):
        channel_id = self.id_generator.generate_viable_id()
        voice_ids = self.id_generator.generate_viable_id_group(4)
        voice_channels: list[VoiceChannel] = _generate_voice_channels(voice_ids, channel_id)
        channel: ScrimChannel = ScrimChannel(channel_id, self._GUILD_ID, *voice_channels)
        actual = self.connection.add_channel(channel)
        self.assertEqual(channel_id, actual.channel_id)
        self._assert_has_voices(actual, voice_ids)

    def test_exists_text_given_not_registered_id_then_none_returned(self):
        channel_id = self.id_generator.generate_nonviable_id()
        self.assertIsNone(self.connection.exists_text(channel_id))

    def test_exists_text_given_registered_id_then_channel_data_returned(self):
        channel_id = self.id_generator.generate_viable_id()
        voice_ids = self.id_generator.generate_viable_id_group(4)
        self._insert_channel(channel_id, *voice_ids)
        actual = self.connection.exists_text(channel_id)
        self.assertEqual(channel_id, actual.channel_id)
        self._assert_has_voices(actual, voice_ids)

    def test_exists_voice_given_not_registered_id_then_none_returned(self):
        channel_id = self.id_generator.generate_nonviable_id()
        self.assertIsNone(self.connection.exists_voice(channel_id))

    def test_exists_voice_given_registered_id_then_channel_data_returned(self):
        channel_id = self.id_generator.generate_nonviable_id()
        parent_id = self.id_generator.generate_viable_id()
        self._insert_channel(parent_id, channel_id)
        actual = self.connection.exists_voice(channel_id).voice_channels
        self.assertIn(channel_id, [channel.channel_id for channel in actual])

    def _insert_channel(self, channel_id, *voice_ids):
        voice_channels: list[VoiceChannel] = _generate_voice_channels(voice_ids, channel_id)
        channel: ScrimChannel = ScrimChannel(channel_id, self._GUILD_ID, *voice_channels)
        with self.master.get_session() as session:
            session.add(channel)

    def _assert_has_voices(self, actual: ScrimChannel, voice_ids):
        for voice_id, voice_channel in zip(voice_ids, actual.voice_channels):
            self.assertEqual(voice_id, voice_channel.channel_id)
            self.assertEqual(actual.channel_id, voice_channel.parent_channel_id)

    def _assert_channel_in_database(self, channel_id, voice_ids):
        with self.master.get_session() as session:
            channel = session.query(ScrimChannel).filter(ScrimChannel.channel_id == channel_id).one()
            self._assert_has_voices(channel, voice_ids)
