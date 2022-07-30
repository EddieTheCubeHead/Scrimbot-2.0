__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, call, AsyncMock

from Bot.Matchmaking.TeamCreation.ClearTeamsStrategy import ClearTeamsStrategy
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestClearTeamsStrategy(AsyncUnittestBase):

    def setUp(self) -> None:
        self.creation_strategy = ClearTeamsStrategy()
        self.scrim_manager = MagicMock()
        self.teams_manager = MagicMock()
        self.scrim_manager.teams_manager = self.teams_manager
        self.scrim_manager.message = AsyncMock()
        self.all_players = []
        self.mock_participants = MagicMock()
        self.mock_participants.members = self.all_players
        self.teams_manager.get_standard_teams.return_value = [self.mock_participants]

    async def test_create_teams_when_called_then_only_clear_step_called_and_new_joining_reactions_set(self):
        self._setup_game(5)
        self._add_players(10)
        await self.creation_strategy.create_teams(self.scrim_manager)
        self.teams_manager.set_team.assert_not_called()
        self.teams_manager.clear_teams.assert_called()
        self.scrim_manager.message.clear_reactions.assert_called()

    async def test_create_teams_when_called_with_game_with_different_team_count_then_correct_amount_of_emojis_added(self):
        player_count = 4
        for team_count in range(1, 10):
            with self.subTest(f"Setting team joining emojis after clearing teams ({team_count} teams)"):
                self._setup_game(player_count, player_count, team_count)
                self.all_players.clear()
                self._add_players(player_count * team_count)
                await self.creation_strategy.create_teams(self.scrim_manager)
                calls = self.scrim_manager.message.add_reaction.call_args_list
                for expected_team in range(1, team_count + 1):
                    self.assertIn(call(emoji=f"{expected_team}\u20E3"), calls)
                calls.clear()

    def _setup_game(self, min_players: int, max_players: int = None, team_count: int = 2):
        mock_game = MagicMock()
        mock_game.min_team_size = min_players
        mock_game.max_team_size = min_players if max_players is None else max_players
        mock_game.team_count = team_count
        self.teams_manager.game = mock_game

    def _add_players(self, amount: int):
        for _ in range(amount):
            self.all_players.append(MagicMock())
