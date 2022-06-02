__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional
from unittest.mock import MagicMock

from Bot.DataClasses.Game import Game
from Bot.DataClasses.User import User
from Bot.DataClasses.UserRating import UserRating, DEFAULT_RATING
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

    def test_build_when_rating_received_then_embed_title_and_description_set_based_on_user(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self.assertEqual("Player statistics", actual_embed.title)
        self.assertEqual(f"<@{user.user_id}>", actual_embed.description)

    def test_build_when_game_received_then_embed_author_set_as_game(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self.assertEqual(game.name, actual_embed.author.name)

    def _create_mock_game(self, game_name: str) -> Game:
        mock_game = MagicMock()
        mock_game.name = game_name
        mock_game.icon = f"{game_name}Icon"
        mock_game.colour = self.id_mocker.generate_viable_id()
        return mock_game

    def _create_mock_user(self, user_id: int) -> User:
        mock_user = MagicMock()
        mock_user.user_id = user_id
        return mock_user

    def _create_mock_rating(self, game: Game, user: User, rating: int = DEFAULT_RATING) -> UserRating:
        mock_rating = MagicMock()
        mock_rating.game = game
        mock_rating.game_name = game.name
        mock_rating.user = user
        mock_rating.user_id = user.user_id
        mock_rating.rating = rating
        return mock_rating
