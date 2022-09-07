__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.DataClasses.Team import Team
from Bot.DataClasses.UserScrimResult import Result
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
        self.mock_result_converter = MagicMock()
        self.mock_guild_converter = MagicMock()
        self.mock_change_calculator = MagicMock()
        self.service = ResultHandler(self.mock_connection, self.mock_result_converter, self.mock_guild_converter,
                                     self.mock_change_calculator)
        self.mocked_teams = []

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ResultHandler)

    def test_save_results_given_two_team_scrim_when_winner_and_loser_present_then_results_saved_correctly(self):
        result = self._create_results(("Team 1",), ("Team 2",))
        self.mock_teams_manager.get_game_teams.return_value = self.mocked_teams
        self.service.save_result(self.mock_context, result)
        added_scrim = self.mock_connection.add_scrim.call_args[0][0]
        self.assertEqual("Team 1", added_scrim.teams[0].team.name)
        self.assertEqual("Team 2", added_scrim.teams[1].team.name)
        self.assertEqual(1, added_scrim.teams[0].placement)
        self.assertEqual(2, added_scrim.teams[1].placement)

    def test_save_results_given_two_team_scrim_when_tie_result_then_results_saved_correctly(self):
        result = self._create_results(("Team 1", "Team 2"))
        self.mock_teams_manager.get_game_teams.return_value = self.mocked_teams
        self.service.save_result(self.mock_context, result)
        added_scrim = self.mock_connection.add_scrim.call_args[0][0]
        self.assertEqual("Team 1", added_scrim.teams[0].team.name)
        self.assertEqual("Team 2", added_scrim.teams[1].team.name)
        self.assertEqual(1, added_scrim.teams[0].placement)
        self.assertEqual(1, added_scrim.teams[1].placement)

    def test_save_results_given_two_team_scrim_when_unregistered_result_then_results_saved_correctly(self):
        result = None
        self.mocked_teams = [self._create_mock_team("Team 1"), self._create_mock_team("Team 2")]
        self.mock_teams_manager.get_game_teams.return_value = self.mocked_teams
        self.service.save_result(self.mock_context, result)
        added_scrim = self.mock_connection.add_scrim.call_args[0][0]
        self.assertIn("Team 1", [scrim_team.team.name for scrim_team in added_scrim.teams])
        self.assertIn("Team 2", [scrim_team.team.name for scrim_team in added_scrim.teams])
        self.assertTrue(all([scrim_team.placement == 0 for scrim_team in added_scrim.teams]))

    def test_save_results_given_two_team_scrim_when_called_then_user_personal_results_saved(self):
        result = self._create_results(("Team 1",), ("Team 2",))
        mock_guild = MagicMock()
        self.mock_guild_converter.get_guild.return_value = mock_guild
        self.mock_teams_manager.get_game_teams.return_value = self.mocked_teams
        self.service.save_result(self.mock_context, result)
        created_scrim = self.mock_connection.add_scrim.call_args[0][0]
        for player in self.mocked_teams[0].members:
            self.mock_result_converter.update_user_rating.assert_any_call(0, Result.WIN, player, created_scrim,
                                                                          mock_guild)
        for player in self.mocked_teams[1].members:
            self.mock_result_converter.update_user_rating.assert_any_call(0, Result.LOSS, player, created_scrim,
                                                                          mock_guild)

    def test_save_results_given_given_two_team_scrim_when_using_flat_rating_change_used_then_ratings_updated(self):
        result = self._create_results(("Team 1",), ("Team 2",))
        mock_changes = {user: 25 for user in result[0][0].members} | {user: -25 for user in result[1][0].members}
        self.mock_change_calculator.calculate_changes.return_value = mock_changes
        mock_guild = MagicMock()
        self.mock_guild_converter.get_guild.return_value = mock_guild
        self.mock_teams_manager.get_game_teams.return_value = self.mocked_teams
        self.service.save_result(self.mock_context, result)
        created_scrim = self.mock_connection.add_scrim.call_args[0][0]
        for player in self.mocked_teams[0].members:
            self.mock_result_converter.update_user_rating.assert_any_call(25, Result.WIN, player, created_scrim,
                                                                          mock_guild)
        for player in self.mocked_teams[1].members:
            self.mock_result_converter.update_user_rating.assert_any_call(-25, Result.LOSS, player, created_scrim,
                                                                          mock_guild)

    def _create_results(self, *team_groups: tuple[str, ...]) -> ScrimResult:
        result_list = []
        for team_group in team_groups:
            result_list.append(self._create_result_group(team_group))
        flattened_teams = [team for team_group in result_list for team in team_group]
        flattened_players = [player for team in flattened_teams for player in team.members]
        self.mock_change_calculator.calculate_changes.return_value = {player: 0 for player in flattened_players}
        return result_list

    def _create_result_group(self, result_group: tuple[str, ...]) -> tuple[Team]:
        teams = []
        for team_name in result_group:
            mocked_team = self._create_mock_team(team_name)
            self.mocked_teams.append(mocked_team)
            teams.append(mocked_team)
        return tuple(teams)

    @staticmethod
    def _create_mock_team(name: str, size: int = 5) -> Team:
        mock_team = Team(name)
        players = []
        for _ in range(size):
            players.append(MagicMock())
        mock_team.members = players
        return mock_team
