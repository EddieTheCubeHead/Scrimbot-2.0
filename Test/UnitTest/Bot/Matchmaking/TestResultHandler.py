__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.DataClasses.Team import Team
from Bot.Matchmaking.ResultHandler import ResultHandler
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestResultHandler(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_context = MagicMock()
        self.mock_scrim = MagicMock()
        self.mock_context.scrim = self.mock_scrim
        self.mock_teams_manager = MagicMock()
        self.mock_scrim.teams_manager = self.mock_teams_manager
        self.mock_connection = MagicMock()
        self.service = ResultHandler(self.mock_connection)
        self.mocked_teams = []
        self.mock_teams_manager.get_game_teams.return_value = self.mocked_teams

    def test_save_results_given_two_team_scrim_when_winner_and_loser_present_then_results_saved_correctly(self):
        result = self._create_results(("Team 1",), ("Team 2",))
        self.service.save_result(self.mock_context, result)
        added_scrim = self.mock_connection.add_scrim.call_args[0][0]
        self.assertEqual("Team 1", added_scrim.teams[0].team.name)
        self.assertEqual("Team 2", added_scrim.teams[1].team.name)
        self.assertEqual(1, added_scrim.teams[0].placement)
        self.assertEqual(2, added_scrim.teams[1].placement)

    def _create_results(self, *team_groups: tuple[str, ...]) -> ScrimResult:
        result_list = []
        for team_group in team_groups:
            result_list.append(self._create_result_group(team_group))
        return result_list

    def _create_result_group(self, result_group: tuple[str, ...]) -> tuple[Team]:
        teams = []
        for team_name in result_group:
            self.mocked_teams.append(team_name)
            teams.append(Team(team_name))
        return tuple(teams)
