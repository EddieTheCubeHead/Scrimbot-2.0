__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.Game import Game
from Bot.EmbedSystem.RatingEmbedBuilder import RatingEmbedBuilder
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestRatingEmbedBuilder(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.builder = RatingEmbedBuilder()
        self.ctx = MagicMock()

    def test_build_given_file_imported_then_instance_dependency_created(self):
        self._assert_instance_dependency(RatingEmbedBuilder)

    def test_build_when_game_received_then_embed_author_set_as_game(self):
        game = self._create_mock_game(self.id_mocker.generate_viable_id())

    def _create_mock_game(self, game_name: int) -> Game:
        mock_game = MagicMock()
        mock_game.name = str(game_name)
        mock_game.icon = f"{game_name}Icon"
        mock_game.colour = game_name
        return mock_game
