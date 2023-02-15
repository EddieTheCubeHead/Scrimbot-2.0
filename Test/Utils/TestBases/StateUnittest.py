__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from discord import Embed, Color

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Team import Team
from Src.Bot.DataClasses.User import User
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_mock_player(user_id):
    return User(user_id=user_id)


def _create_participant_team(team: Team, placement: int = None):
    participant_team = ParticipantTeam(placement, 5)
    participant_team.team = team
    return participant_team


class StateUnittest(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_builder = TestIdGenerator()

    def setUp(self) -> None:
        self.participants = _create_participant_team(Team(ScrimTeamsManager.PARTICIPANTS))
        self.spectators = _create_participant_team(Team(ScrimTeamsManager.SPECTATORS))
        self.queue = _create_participant_team(Team(ScrimTeamsManager.QUEUE))
        self.team_1 = _create_participant_team(Team("Team 1", min_size=5))
        self.team_2 = _create_participant_team(Team("Team 2", min_size=5))
        self.name_mappings = {}
        self.scrim = MagicMock()
        self.scrim.teams = [self.participants, self.spectators, self.queue, self.team_1, self.team_2]
        self.mock_game = self.create_mock_game("Test", 2, 5)
        self.scrim.game = self.mock_game

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
            self.participants.team.members.append(_create_mock_player(user_id))

    def add_queued(self, *user_ids: int):
        for user_id in user_ids:
            self.queue.team.members.append(_create_mock_player(user_id))

    def add_spectators(self, *user_ids: int):
        for user_id in user_ids:
            self.spectators.team.members.append(_create_mock_player(user_id))

    def add_team_1(self, *user_ids):
        for user_id in user_ids:
            self.team_1.team.members.append(_create_mock_player(user_id))

    def add_team_2(self, *user_ids):
        for user_id in user_ids:
            self.team_2.team.members.append(_create_mock_player(user_id))

