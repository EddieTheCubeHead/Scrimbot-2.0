__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Matchmaking.TeamCreation.TeamCreationStrategy import TeamCreationStrategy
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class MockTeamCreationStrategy(TeamCreationStrategy):

    def _create_teams_hook(self, teams_manager):
        pass


class TestTeamCreationStrategy(AsyncUnittestBase):

    async def test_create_teams_when_called_then_teams_cleared_first_and_reactions_cleared(self):
        strategy = MockTeamCreationStrategy()
        scrim_manager = MagicMock()
        teams_manager = MagicMock()
        scrim_manager.teams_manager = teams_manager
        scrim_manager.message = AsyncMock()
        await strategy.create_teams(scrim_manager)
        teams_manager.clear_teams.assert_called()
        scrim_manager.message.clear_reactions.assert_called()
