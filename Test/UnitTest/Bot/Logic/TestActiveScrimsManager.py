__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_mock_game(team_count, min_player_count, max_player_count=None):
    mock_game = MagicMock()
    mock_game.team_count = team_count
    mock_game.min_team_size = min_player_count
    mock_game.max_team_size = max_player_count if max_player_count is not None else min_player_count
    return mock_game


@unittest.skip("Waiting for scrim state rewrite")
class TestActiveScrimsManager(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.manager = ActiveScrimsManager()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ActiveScrimsManager)

    def test_try_get_scrim_given_channel_id_with_scrim_then_scrim_returned(self):
        mock_scrim = MagicMock()
        test_channel_id = self.id_generator.generate_viable_id()
        self.manager.scrims[test_channel_id] = mock_scrim
        self.assertEqual(mock_scrim, self.manager.try_get_scrim(test_channel_id))

    def test_try_get_scrim_given_channel_id_without_scrim_then_none_returned(self):
        self.assertIsNone(self.manager.try_get_scrim(self.id_generator.generate_nonviable_id()))

    def test_create_scrim_given_scrim_channel_and_game_then_scrim_manager_created_correctly(self):
        mock_game = _create_mock_game(2, 5)
        mock_scrim_channel = self._create_mock_channel()
        scrim = self.manager.create_scrim(mock_scrim_channel, mock_game)
        self.assertEqual(mock_game, scrim.teams_manager.game)
        self._assert_scrim_created_correctly(mock_scrim_channel, mock_game)

    def test_drop_given_existing_scrim_then_scrim_removed_from_dict(self):
        mock_scrim = MagicMock()
        test_channel_id = self.id_generator.generate_viable_id()
        self.manager.scrims[test_channel_id] = mock_scrim
        mock_scrim.message.channel.id = test_channel_id
        self.manager.drop(mock_scrim)
        self.assertNotIn(test_channel_id, self.manager.scrims)

    def _create_mock_channel(self) -> ScrimChannel:
        mock_channel = MagicMock()
        mock_channel.channel_id, mock_channel.guild_id = self.id_generator.generate_viable_id_group(2)
        mock_channel.voice_channels = []
        return mock_channel

    def _assert_scrim_created_correctly(self, mock_scrim_channel: ScrimChannel, mock_game: Game):
        created_scrim = self.manager.scrims[mock_scrim_channel.channel_id]
        self.assertEqual(mock_game, created_scrim.teams_manager.game)
