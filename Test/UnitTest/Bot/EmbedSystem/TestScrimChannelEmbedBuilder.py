__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Test.Utils.TestBases.EmbedUnittest import EmbedUnittest
from Bot.EmbedSystem.ScrimChannelEmbedBuilder import ScrimChannelEmbedBuilder


class TestScrimChannelEmbedBuilder(EmbedUnittest):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.builder = ScrimChannelEmbedBuilder()
        self.ctx = MagicMock()

    def test_build_given_file_imported_then_instance_dependency_created(self):
        self._assert_instance_dependency(ScrimChannelEmbedBuilder)

    def test_build_given_channel_then_embed_title_set_and_first_field_populated(self):
        scrim_channel = self._create_mock_text_channel()
        embed = self.builder.build(self.ctx, scrim_channel)
        self.assertEqual("New scrim channel registered successfully!", embed.title)
        self.assertEqual("Channel data:", embed.description)
        self._assert_correct_fields(embed, ("Text channel", f"<#{scrim_channel.channel_id}>"))

    def test_build_given_only_text_channel_then_embed_only_has_one_field(self):
        scrim_channel = self._create_mock_text_channel()
        embed = self.builder.build(self.ctx, scrim_channel)
        self.assertEqual(1, len(embed.fields))

    def test_build_given_lobby_voice_channel_then_embed_description_set_and_field_created(self):
        voice_channel = self._create_mock_voice_channel(0)
        scrim_channel = self._create_mock_text_channel(voice_channel)
        embed = self.builder.build(self.ctx, scrim_channel)
        self._assert_correct_fields(embed, ("Text channel", f"<#{scrim_channel.channel_id}>"),
                                    ("Voice lobby", f"<#{voice_channel.channel_id}>"))

    def test_build_given_two_team_voice_channels_then_correct_fields_created(self):
        voice_channels = self._create_mock_voice_channels(2, 1)
        scrim_channel = self._create_mock_text_channel(*voice_channels)
        embed = self.builder.build(self.ctx, scrim_channel)
        self._assert_correct_fields(embed, ("Text channel", f"<#{scrim_channel.channel_id}>"),
                                    ("Team 1 voice", f"<#{voice_channels[0].channel_id}>"),
                                    ("Team 2 voice", f"<#{voice_channels[1].channel_id}>"))

    def test_build_given_lobby_and_four_team_voice_channels_then_correct_fields_created(self):
        voice_channels = self._create_mock_voice_channels(5)
        scrim_channel = self._create_mock_text_channel(*voice_channels)
        embed = self.builder.build(self.ctx, scrim_channel)
        self._assert_correct_fields(embed, ("Text channel", f"<#{scrim_channel.channel_id}>"),
                                    ("Voice lobby", f"<#{voice_channels[0].channel_id}>"),
                                    ("Team 1 voice", f"<#{voice_channels[1].channel_id}>"),
                                    ("Team 2 voice", f"<#{voice_channels[2].channel_id}>"),
                                    ("Team 3 voice", f"<#{voice_channels[3].channel_id}>"),
                                    ("Team 4 voice", f"<#{voice_channels[4].channel_id}>"))

    def _create_mock_text_channel(self, *_voice_channels):
        channel_id, guild_id = self.id_mocker.generate_viable_id_group(2)
        scrim_channel = ScrimChannel(channel_id, guild_id, *_voice_channels)
        return scrim_channel

    def _create_mock_voice_channel(self, team_number: int):
        channel_id, guild_id = self.id_mocker.generate_viable_id_group(2)
        scrim_channel = VoiceChannel(channel_id, guild_id, team_number)
        return scrim_channel

    def _create_mock_voice_channels(self, amount: int, first_team_number: int = 0):
        voice_channels = []
        for team_number in range(first_team_number, amount + first_team_number):
            voice_channels.append(self._create_mock_voice_channel(team_number))
        return voice_channels
