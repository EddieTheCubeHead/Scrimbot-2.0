__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Src.Bot.Cogs.Helpers.ScrimTeamOperationService import ScrimTeamOperationService
from Src.Bot.Matchmaking.TeamCreation.TeamCreationStrategy import TeamCreationStrategy
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.bot_dependency_patcher import mock_dependency


class MockTeamCreationStrategy(TeamCreationStrategy):

    def _create_teams_hook(self, teams_manager):
        pass


class TestTeamCreationStrategy(AsyncUnittestBase):

    def setUp(self) -> None:
        self.team_service = MagicMock()
        with mock_dependency(ScrimTeamOperationService, self.team_service):
            self.strategy = MockTeamCreationStrategy()

    async def test_create_teams_when_called_then_teams_cleared_first_and_reactions_cleared(self):
        scrim = AsyncMock()
        message = AsyncMock()
        await self.strategy.create_teams(scrim, message)
        self.team_service.clear_teams.assert_called()
        message.clear_reactions.assert_called()
