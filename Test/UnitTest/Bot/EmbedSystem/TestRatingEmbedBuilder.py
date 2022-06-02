__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional
from unittest.mock import MagicMock

from discord import Color

from Bot.DataClasses.Game import Game
from Bot.DataClasses.User import User
from Bot.DataClasses.UserRating import UserRating, DEFAULT_RATING
from Bot.EmbedSystem.RatingEmbedBuilder import RatingEmbedBuilder
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
        mock_member.display_avatar.url = "test_url"
        user.member = mock_member
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self.assertEqual(mock_member.display_avatar.url, actual_embed.thumbnail.url)

    def test_build_when_rating_with_no_games_played_received_then_rating_and_stats_displayed(self):
        game = self._create_mock_game(str(self.id_mocker.generate_viable_id()))
        user = self._create_mock_user(self.id_mocker.generate_viable_id())
        mock_member = MagicMock()
        mock_member.display_avatar.url = "test_url"
        user.member = mock_member
        rating = self._create_mock_rating(game, user)
        actual_embed = self.builder.build(self.ctx, rating)
        self._assert_correct_fields(actual_embed, ("Games played", "0", True), ("Wins", "0", True),
                                    ("Losses", "0", True), ("Ties", "0", True), ("Unrecorded", "0", True),
                                    ("Rating", f"{DEFAULT_RATING}", True))

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

    def _create_mock_rating(self, game: Game, user: User, rating: int = DEFAULT_RATING, wins: int = 0, losses: int = 0) \
            -> UserRating:
        mock_rating = MagicMock()
        mock_rating.game = game
        mock_rating.game_name = game.name
        mock_rating.user = user
        mock_rating.user_id = user.user_id
        mock_rating.rating = rating
        self._insert_games(mock_rating, wins, losses)
        return mock_rating

    def _insert_games(self, rating: UserRating, wins: int = 0, losses: int = 0):
        rating.user.teams = []
        for _ in range(wins):
            rating.user.teams.append(self._create_result(1))
        for _ in range(losses):
            rating.user.teams.append(self._create_result(2))

    def _create_result(self, placement: int):
        scrim = MagicMock()
        scrim.placement = placement
        team = MagicMock()
        team.scrims = [scrim]
        return scrim
