__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.TestBases.UnittestBase import UnittestBase

from Bot.Converters.Helpers.ChannelGroupParser import ChannelGroupParser
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestChannelGroupParser(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.group_parser = ChannelGroupParser()
        self.mock_group = MagicMock()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ChannelGroupParser)

    def test_parse_group_given_channel_group_with_one_channel_returns_lobby(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 1")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 0, 0)

    def test_parse_group_given_channel_group_with_two_channels_then_teams_one_and_two_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Radiant", "Dire")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 1, 2)

    def test_parse_group_given_channel_group_with_lobby_and_two_team_channels_then_correct_teams_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 1", "Lobby", "Team 2")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 0, 2)

    def test_parse_group_given_channel_group_with_three_team_channels_then_correct_teams_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 1", "Team 3", "Team 2")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 1, 3)

    def test_parse_group_given_channel_group_with_three_team_channels_and_lobby_then_correct_teams_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 2", "Lobby", "Team 3", "Team 1")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 0, 3)

    def test_parse_group_given_lobby_channel_named_with_team_prefix_then_correct_teams_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 2", "Team Lobby", "Team 3", "Team 1")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 0, 3)

    def test_parse_group_given_lobby_channel_named_with_team_prefix_and_suffix_then_correct_teams_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 2 ch", "Team 0 ch", "Team 3 ch", "Team 1 ch")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 0, 3)

    def test_parse_group_given_lobby_channel_name_starts_with_team_channel_name_then_correct_teams_returned(self):
        self.mock_group.voice_channels = self._create_mock_voices("Team 2", "Team 1 but lobby", "Team 1")
        actual_channels = self.group_parser.parse(self.mock_group)
        self._assert_correct_group(actual_channels, 0, 2)
        self.assertEqual("Team 1 but lobby", actual_channels[0][0].name)

    def _create_mock_voice(self, channel_name):
        mock_channel = MagicMock()
        mock_channel.id = self.id_mocker.generate_viable_id()
        mock_channel.name = channel_name
        return mock_channel

    def _assert_correct_group(self, actual_channels, first_team, last_team):
        self.assertEqual(last_team - first_team + 1, len(actual_channels))
        for channel, expected_team in zip(actual_channels, range(first_team, last_team)):
            self.assertEqual(expected_team, channel[1])

    def _create_mock_voices(self, *names):
        mock_voices = []
        for name in names:
            mock_voices.append(self._create_mock_voice(name))
        return mock_voices
