__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock, call, AsyncMock

from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Team import PARTICIPANTS, SPECTATORS, QUEUE
from Src.Bot.Matchmaking.TeamCreation.ClearTeamsStrategy import ClearTeamsStrategy
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


def _create_team(name: str) -> ParticipantTeam:
    mock_participant_team = MagicMock()
    mock_team = MagicMock()
    mock_team.members = []
    mock_team.name = name
    mock_participant_team.max_size = 0
    mock_participant_team.team = mock_team
    return mock_participant_team


class TestClearTeamsStrategy(AsyncUnittestBase):

    def setUp(self) -> None:
        self.creation_strategy = ClearTeamsStrategy()
        self.scrim = MagicMock()
        self.scrim.teams = [_create_team(name) for name in (PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")]
        self.message = AsyncMock()
        self.all_players = []
        self.scrim.teams[0].team.members = self.all_players

    async def test_create_teams_when_called_then_only_clear_step_called_and_new_joining_reactions_set(self):
        self._setup_game(5)
        self._add_players(10)
        await self.creation_strategy.create_teams(self.scrim, self.message)
        self.message.clear_reactions.assert_called()

    async def test_create_teams_when_called_with_game_with_different_team_count_then_correct_amount_of_emojis_added(self):
        player_count = 4
        for team_count in range(1, 10):
            with self.subTest(f"Setting team joining emojis after clearing teams ({team_count} teams)"):
                self._setup_game(player_count, player_count, team_count)
                self.all_players.clear()
                self._add_players(player_count * team_count)
                await self.creation_strategy.create_teams(self.scrim, self.message)
                calls = self.message.add_reaction.call_args_list
                for expected_team in range(1, team_count + 1):
                    self.assertIn(call(emoji=f"{expected_team}\u20E3"), calls)
                calls.clear()

    def _setup_game(self, min_players: int, max_players: int = None, team_count: int = 2):
        mock_game = MagicMock()
        mock_game.min_team_size = min_players
        mock_game.max_team_size = min_players if max_players is None else max_players
        mock_game.team_count = team_count
        self.scrim.game = mock_game

    def _add_players(self, amount: int):
        for _ in range(amount):
            self.all_players.append(MagicMock())
