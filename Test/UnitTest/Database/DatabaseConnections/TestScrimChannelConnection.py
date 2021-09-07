__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Any

from sqlalchemy.exc import NoResultFound

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Database.Core.MasterConnection import MasterConnection
from Utils.ConnectionUnittest import ConnectionUnittest
from Utils.TestIdGenerator import TestIdGenerator
from Utils.UnittestBase import UnittestBase
from Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


def _generate_voice_channels(voice_ids, parent_channel_id) -> list[VoiceChannel]:
    voice_channels: list[VoiceChannel] = []
    for team, voice_id in enumerate(voice_ids):
        voice_channels.append(VoiceChannel(voice_id, parent_channel_id, team))
    return voice_channels


class TestScrimChannelConnection(ConnectionUnittest[ScrimChannel]):

    _GUILD_ID = 1

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.master = MasterConnection(":memory:")

    def setUp(self) -> None:
        self.connection: ScrimChannelConnection = ScrimChannelConnection(self.master)

    def test_init_given_normal_init_then_connection_for_scrim_channel_dataclass_set(self):
        self.assertIn(ScrimChannelConnection, BotDependencyInjector.dependencies)

    def test_get_channel_given_valid_id_then_channel_returned_with_voice_channels(self):
        channel_id = self.id_generator.generate_viable_id()
        voice_ids = self.id_generator.generate_viable_id_group(4)
        self._insert_channel(channel_id, voice_ids)
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

    def _insert_channel(self, channel_id, voice_ids):
        voice_channels: list[VoiceChannel] = _generate_voice_channels(voice_ids, channel_id)
        channel: ScrimChannel = ScrimChannel(channel_id, self._GUILD_ID, *voice_channels)
        with self.master.get_session() as session:
            session.add(channel)

    def _assert_has_voices(self, actual: ScrimChannel, voice_ids):
        for voice_id in voice_ids:
            self.assertIn(voice_id, [voice.channel_id for voice in actual.voice_channels])

    def _assert_channel_in_database(self, channel_id, voice_ids):
        with self.master.get_session() as session:
            channel = session.query(ScrimChannel).filter(ScrimChannel.channel_id == channel_id).one()
            self._assert_has_voices(channel, voice_ids)
