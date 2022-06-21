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
        self.service = ResultHandler()

    def test_save_results_given_two_team_scrim_when_winner_and_loser_present_then_results_saved_correctly(self):
        results = self._create_results(("Team 1",), ("Team 2",))

    def _create_results(self, *team_groups: tuple[str, ...]) -> ScrimResult:
        result_list = []
        for team_group in team_groups:
            result_list.append(self._create_result_group(team_group))
        return result_list

    @staticmethod
    def _create_result_group(result_group: tuple[str, ...]) -> tuple[Team]:
        teams = []
        for team_name in result_group:
            teams.append(Team(team_name))
        return tuple(teams)
