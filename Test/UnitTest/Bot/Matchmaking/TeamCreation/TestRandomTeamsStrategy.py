__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock, AsyncMock

from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Team import PARTICIPANTS, SPECTATORS, QUEUE
from Src.Bot.Matchmaking.TeamCreation.RandomTeamsStrategy import RandomTeamsStrategy
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


def _create_team(name: str) -> ParticipantTeam:
    mock_participant_team = MagicMock()
    mock_team = MagicMock()
    mock_team.members = []
    mock_team.name = name
    mock_participant_team.max_size = 0
    mock_participant_team.team = mock_team
    return mock_participant_team


class TestRandomTeamsStrategy(AsyncUnittestBase):

    def setUp(self) -> None:
        self.converter = MagicMock()
        self.creation_strategy = RandomTeamsStrategy(self.converter)
        self.scrim = MagicMock()
        self.scrim.teams = [_create_team(name) for name in (PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")]
        self.message = AsyncMock()
        self.all_players = []
        self.scrim.teams[0].team.members = self.all_players

    async def test_create_teams_when_given_strictly_sized_teams_then_all_teams_filled(self):
        self._setup_game(5)
        self._add_players(10)
        await self.creation_strategy.create_teams(self.scrim, self.message)
        remove_calls = self.converter.remove_from_team.call_args_list
        add_calls = self.converter.add_to_team.call_args_list
        self.assertEqual(10, len(remove_calls))
        self.assertEqual(10, len(add_calls))
        self.converter.clear_teams.assert_called()

    def _setup_game(self, min_players: int, max_players: int = None, team_count: int = 2):
        mock_game = MagicMock()
        mock_game.min_team_size = min_players
        mock_game.max_team_size = min_players if max_players is None else max_players
        mock_game.team_count = team_count
        self.scrim.game = mock_game

    def _add_players(self, amount: int):
        for _ in range(amount):
            self.all_players.append(MagicMock())
