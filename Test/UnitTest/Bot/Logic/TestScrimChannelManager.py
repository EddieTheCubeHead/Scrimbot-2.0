__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Src.Bot.DataClasses.VoiceChannel import VoiceChannel
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Src.Bot.Logic.ScrimChannelManager import ScrimChannelManager
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimChannelManager(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.manager = ScrimChannelManager()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimChannelManager)

    def test_enumerate_teams_given_a_list_with_no_lobby_then_teams_get_sequential_numbers_starting_from_one(self):
        guild_id = self.id_mocker.generate_viable_id()
        voice_channels = self._generate_voice_channels(guild_id, 5)
        voice_channels = self.manager.enumerate_teams(voice_channels)
        for voice_channel, team in zip(voice_channels, range(1, 6)):
            self.assertEqual(voice_channel.team_number, team)

    def test_enumerate_teams_given_a_list_with_lobby_then_teams_get_sequential_numbers_starting_from_zero(self):
        guild_id = self.id_mocker.generate_viable_id()
        voice_channels = self._generate_voice_channels(guild_id, 8)
        lobby_channel = voice_channels[4]
        lobby_channel.team_number = 0
        voice_channels = self.manager.enumerate_teams(voice_channels)
        for voice_channel, team in zip(voice_channels, range(0, 8)):
            self.assertEqual(voice_channel.team_number, team)

    def _generate_voice_channels(self, guild_id: int, channel_amount: int):
        voice_channels = []
        for channel_id in self.id_mocker.generate_viable_id_group(channel_amount):
            voice_channels.append(VoiceChannel(channel_id, guild_id))
        return voice_channels
