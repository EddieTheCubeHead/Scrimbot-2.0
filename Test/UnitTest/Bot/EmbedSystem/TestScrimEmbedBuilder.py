__version__ = "ver"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from discord import Embed, Color

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Utils.TestBases.EmbedUnittest import EmbedUnittest
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimEmbedBuilder(EmbedUnittest):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_builder = TestIdGenerator()

    def setUp(self) -> None:
        self.user_nickname_service = MagicMock()
        self.user_nickname_service.get_name.side_effect = lambda _, x: self.name_mappings[x]
        self.name_mappings = {}
        self.builder = ScrimEmbedBuilder(self.user_nickname_service)
        self.scrim_manager = MagicMock()
        self.teams_manager = MagicMock()
        self.scrim_manager.teams_manager = self.teams_manager
        self.participants = Team(ScrimTeamsManager.PARTICIPANTS)
        self.spectators = Team(ScrimTeamsManager.SPECTATORS)
        self.teams_manager.get_standard_teams = self.mock_standard_teams
        self.teams_manager.get_game_teams.return_value = []
        self.mock_game = self._create_mock_game("Test", 2, 5)
        self.teams_manager.game = self.mock_game
        self.context = MagicMock()

    def test_build_given_scrim_with_no_participants_then_empty_scrim_embed_returned(self):
        actual = self.builder.build(self.context, self.scrim_manager)
        self._assert_game_fields(actual)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Looking for players, {self.mock_game.team_count * self.mock_game.min_team_size} required.",
                         actual.description)
        self._assert_correct_fields(actual, ("Participants", "__empty__"),
                                            ("Spectators", "__empty__"))
        self.assertEqual("To join players react \U0001F3AE To join spectators react \U0001F441", actual.footer.text)

    def test_build_given_scrim_with_participants_then_scrim_embed_with_participants_returned(self):
        self._add_participants("Tester 1", "Tester 2")
        actual = self.builder.build(self.context, self.scrim_manager)
        self._assert_game_fields(actual)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Looking for players, {self.mock_game.team_count * self.mock_game.min_team_size} required.",
                         actual.description)
        self._assert_correct_fields(actual, ("Participants", "Tester 1/nTester 2"),
                                            ("Spectators", "__empty__"))
        self.assertEqual("To join players react \U0001F3AE To join spectators react \U0001F441", actual.footer.text)

    def mock_standard_teams(self):
        return [self.participants, self.spectators]

    def _create_mock_game(self, name, team_count, min_team_size, max_team_size=None) -> Game:
        mock_game = MagicMock()
        mock_game.name = name
        mock_game.team_count = team_count
        mock_game.min_team_size = min_team_size
        mock_game.max_team_size = max_team_size if max_team_size is not None else min_team_size
        mock_game.icon = str(self.id_builder.generate_viable_id())
        mock_game.colour = self.id_builder.generate_viable_id()
        return mock_game

    def _assert_game_fields(self, embed: Embed):
        self.assertEqual(f"{self.mock_game.name} scrim", embed.author.name)
        self.assertEqual(self.mock_game.icon, embed.author.icon_url)
        self.assertEqual(Color(self.mock_game.colour), embed.colour)

    def _create_mock_player(self, name):
        mock_player = User(user_id=self.id_builder.generate_viable_id())
        self.name_mappings[mock_player.user_id] = name
        return mock_player

    def _add_participants(self, *names: str):
        for name in names:
            self.participants.members.append(self._create_mock_player(name))