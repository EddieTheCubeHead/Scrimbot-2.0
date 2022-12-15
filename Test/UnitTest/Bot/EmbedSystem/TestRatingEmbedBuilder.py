__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional
from unittest.mock import MagicMock

from discord import Color

from Src.Bot.DataClasses.UserScrimResult import Result
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.User import User
from Src.Bot.DataClasses.UserRating import UserRating, DEFAULT_RATING
from Src.Bot.EmbedSystem.RatingEmbedBuilder import RatingEmbedBuilder
from Utils.TestBases.EmbedUnittest import EmbedUnittest
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestRatingEmbedBuilder(EmbedUnittest):

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
        self.assertEqual(f"<@!{user.user_id}>", actual_embed.description)

    def test_build_when_game_received_then_embed_author_set_as_game(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self.assertEqual(game.name, actual_embed.author.name)
        self.assertEqual(game.icon, actual_embed.author.icon_url)
        self.assertEqual(Color(game.colour), actual_embed.colour)

    def test_build_when_user_received_then_thumbnail_set(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        mock_member = MagicMock()
        mock_member.avatar_url = "test_url"
        user.member = mock_member
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self.assertEqual(mock_member.avatar_url, actual_embed.thumbnail.url)

    def test_build_when_rating_with_no_games_played_received_then_rating_and_stats_displayed(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        mock_member = MagicMock()
        mock_member.avatar_url = "test_url"
        user.member = mock_member
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self._assert_correct_fields(actual_embed, ("Games played", "0", True), ("Wins", "0", True),
                                    ("Losses", "0", True), ("Ties", "0", True), ("Unrecorded", "0", True),
                                    ("Rating", f"{DEFAULT_RATING}", True))

    def test_build_when_rating_with_games_recorded_received_then_rating_and_stats_displayed(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        mock_member = MagicMock()
        mock_member.avatar_url = "test_url"
        user.member = mock_member
        rating = self._create_mock_rating(game, user)
        self._insert_results(rating, 11, 8, 7, 3)
        actual_embed = self.builder.build(self.ctx, rating)
        self._assert_correct_fields(actual_embed, ("Games played", "29", True), ("Wins", "11", True),
                                    ("Losses", "8", True), ("Ties", "7", True), ("Unrecorded", "3", True),
                                    ("Rating", f"{DEFAULT_RATING}", True))

    def _create_mock_game(self, game_name: str) -> Game:
        mock_game = MagicMock()
        mock_game.name = game_name
        mock_game.icon = f"{game_name}Icon"
        mock_game.colour = self.id_mocker.generate_viable_id()
        return mock_game

    @staticmethod
    def _create_mock_user(user_id: int) -> User:
        mock_user = MagicMock()
        mock_user.user_id = user_id
        return mock_user

    def _create_mock_rating(self, game: Game, user: User, rating: int = DEFAULT_RATING, wins: int = 0, losses: int = 0)\
            -> UserRating:
        mock_rating = MagicMock()
        mock_rating.game = game
        mock_rating.game_name = game.name
        mock_rating.user = user
        mock_rating.user_id = user.user_id
        mock_rating.rating = rating
        self._insert_results(mock_rating, wins, losses)
        return mock_rating

    def _insert_results(self, rating: UserRating, wins: int = 0, losses: int = 0, ties: int = 0, unregistered: int = 0):
        rating.results = []
        for _ in range(wins):
            rating.results.append(self._create_result(Result.WIN))
        for _ in range(losses):
            rating.results.append(self._create_result(Result.LOSS))
        for _ in range(ties):
            rating.results.append(self._create_result(Result.TIE))
        for _ in range(unregistered):
            rating.results.append(self._create_result(Result.UNREGISTERED))

    @staticmethod
    def _create_result(placement: Result):
        frozen_rating = MagicMock()
        frozen_rating.result = placement
        return frozen_rating
