__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from discord import Embed, Color

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_mock_player(user_id):
    return User(user_id=user_id)


class StateUnittest(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_builder = TestIdGenerator()

    def setUp(self) -> None:
        self.participants = Team(ScrimTeamsManager.PARTICIPANTS)
        self.spectators = Team(ScrimTeamsManager.SPECTATORS)
        self.queue = Team(ScrimTeamsManager.QUEUE)
        self.team_1 = Team("Team 1", min_size=5)
        self.team_2 = Team("Team 2", min_size=5)
        self.name_mappings = {}
        self.teams_manager = MagicMock()
        self.teams_manager.get_standard_teams = self.mock_standard_teams
        self.teams_manager.get_game_teams = self.mock_game_teams
        self.mock_game = self.create_mock_game("Test", 2, 5)
        self.teams_manager.game = self.mock_game

    def mock_standard_teams(self):
        return [self.participants, self.spectators, self.queue]

    def mock_game_teams(self):
        return [self.team_1, self.team_2]

    def create_mock_game(self, name, team_count, min_team_size, max_team_size=None) -> Game:
        mock_game = MagicMock()
        mock_game.name = name
        mock_game.team_count = team_count
        mock_game.min_team_size = min_team_size
        mock_game.max_team_size = max_team_size if max_team_size is not None else min_team_size
        mock_game.icon = str(self.id_builder.generate_viable_id())
        mock_game.colour = self.id_builder.generate_viable_id()
        return mock_game

    def assert_game_fields(self, embed: Embed):
        self.assertEqual(f"{self.mock_game.name} scrim", embed.author.name)
        self.assertEqual(self.mock_game.icon, embed.author.icon_url)
        self.assertEqual(Color(self.mock_game.colour), embed.colour)

    def add_participants(self, *user_ids: int):
        for user_id in user_ids:
            self.participants.members.append(_create_mock_player(user_id))

    def add_queued(self, *user_ids: int):
        for user_id in user_ids:
            self.queue.members.append(_create_mock_player(user_id))

    def add_spectators(self, *user_ids: int):
        for user_id in user_ids:
            self.spectators.members.append(_create_mock_player(user_id))

