__version__ = "ver"
__author__ = "Eetu Asikainen"

import os
from unittest.mock import MagicMock

from discord import Embed, Color

from Bot.DataClasses.Game import Game
from Bot.DataClasses.ScrimState import ScrimState
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Utils.TestBases.EmbedUnittest import EmbedUnittest
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_mock_player(user_id):
    return User(user_id=user_id)


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
        self.queue = Team(ScrimTeamsManager.QUEUE)
        self.team_1 = Team("Team 1")
        self.team_2 = Team("Team 2")
        self.teams_manager.get_standard_teams = self.mock_standard_teams
        self.teams_manager.get_game_teams = self.mock_game_teams
        self.mock_game = self._create_mock_game("Test", 2, 5)
        self.teams_manager.game = self.mock_game
        self.context = MagicMock()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimEmbedBuilder)

    def test_build_given_scrim_with_no_participants_then_empty_scrim_embed_returned(self):
        self.scrim_manager.state = ScrimState.LFP
        actual = self.builder.build(self.context, self.scrim_manager)
        self._assert_game_fields(actual)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Looking for players, {self.mock_game.team_count * self.mock_game.min_team_size} more "
                         f"required.", actual.description)
        self._assert_correct_fields(actual, ("Participants", "_empty_"),
                                            ("Spectators", "_empty_"))
        self.assertEqual("To join players react \U0001F3AE To join spectators react \U0001F441", actual.footer.text)

    def test_build_given_scrim_with_participants_then_scrim_embed_with_participants_returned_and_no_queue(self):
        self.scrim_manager.state = ScrimState.LFP
        self._add_participants(1, 2)
        actual = self.builder.build(self.context, self.scrim_manager)
        self._assert_game_fields(actual)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Looking for players, {self.mock_game.team_count * self.mock_game.min_team_size - 2} more "
                         f"required.", actual.description)
        self._assert_correct_fields(actual, ("Participants", f"<#1>{os.linesep}<#2>"),
                                            ("Spectators", "_empty_"))
        self.assertEqual("To join players react \U0001F3AE To join spectators react \U0001F441", actual.footer.text)

    def test_build_given_scrim_with_players_in_queue_then_scrim_embed_with_queued_players_returned(self):
        self.scrim_manager.state = ScrimState.LFP
        self._add_participants(1, 2)
        self._add_queued(3)
        actual = self.builder.build(self.context, self.scrim_manager)
        self._assert_game_fields(actual)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Looking for players, {self.mock_game.team_count * self.mock_game.min_team_size - 2} more "
                         f"required.", actual.description)
        self._assert_correct_fields(actual, ("Participants", f"<#1>{os.linesep}<#2>", True),
                                            ("Spectators", "_empty_", True),
                                            ("Queue", "<#3>", True))
        self.assertEqual("To join players react \U0001F3AE To join spectators react \U0001F441", actual.footer.text)

    def test_build_given_scrim_with_spectators_then_scrim_embed_with_spectators_returned(self):
        self.scrim_manager.state = ScrimState.LFP
        self._add_spectators(1, 2)
        actual = self.builder.build(self.context, self.scrim_manager)
        self._assert_game_fields(actual)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Looking for players, {self.mock_game.team_count * self.mock_game.min_team_size} more "
                         f"required.", actual.description)
        self._assert_correct_fields(actual, ("Participants", "_empty_", True),
                                    ("Spectators", f"<#1>{os.linesep}<#2>", True))
        self.assertEqual("To join players react \U0001F3AE To join spectators react \U0001F441", actual.footer.text)

    def mock_standard_teams(self):
        return [self.participants, self.spectators, self.queue]

    def mock_game_teams(self):
        return [self.team_1, self.team_2]

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

    def _add_participants(self, *user_ids: int):
        for user_id in user_ids:
            self.participants.members.append(_create_mock_player(user_id))

    def _add_queued(self, *user_ids: int):
        for user_id in user_ids:
            self.queue.members.append(_create_mock_player(user_id))

    def _add_spectators(self, *user_ids: int):
        for user_id in user_ids:
            self.spectators.members.append(_create_mock_player(user_id))
