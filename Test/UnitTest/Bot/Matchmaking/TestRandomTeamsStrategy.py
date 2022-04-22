__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Matchmaking.RandomTeamsStrategy import RandomTeamsStrategy
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestRandomTeamsStrategy(AsyncUnittestBase):

    def setUp(self) -> None:
        self.creation_strategy = RandomTeamsStrategy()
        self.scrim_manager = MagicMock()
        self.teams_manager = MagicMock()
        self.scrim_manager.teams_manager = self.teams_manager
        self.scrim_manager.message = AsyncMock()
        self.all_players = []
        self.mock_participants = MagicMock()
        self.mock_participants.members = self.all_players
        self.teams_manager.get_standard_teams.return_value = [self.mock_participants]

    async def test_create_teams_when_given_strictly_sized_teams_then_all_teams_filled(self):
        self._setup_game(5)
        self._add_players(10)
        await self.creation_strategy.create_teams(self.scrim_manager)
        calls = self.teams_manager.set_team.call_args_list
        self.assertEqual(10, len(calls))
        self.teams_manager.clear_teams.assert_called()

    def _setup_game(self, min_players: int, max_players: int = None, team_count: int = 2):
        mock_game = MagicMock()
        mock_game.min_team_size = min_players
        mock_game.max_team_size = min_players if max_players is None else max_players
        mock_game.team_count = team_count
        self.teams_manager.game = mock_game

    def _add_players(self, amount: int):
        for _ in range(amount):
            self.all_players.append(MagicMock())
