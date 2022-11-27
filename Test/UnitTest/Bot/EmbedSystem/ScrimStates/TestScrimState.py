__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
from unittest.mock import MagicMock

from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team, PARTICIPANTS, SPECTATORS, QUEUE
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.StateUnittest import UnittestBase


class BasicStateImplementation(ScrimState):

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        pass

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        pass

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        pass

    @property
    def description(self) -> str:
        return 'description'


def _create_mock_team(*member_ids: int) -> Team:
    mock_team = MagicMock()
    mock_team.members = []
    for member_id in member_ids:
        mock_member = MagicMock()
        mock_member.user_id = member_id
        mock_team.members.append(mock_member)
    return mock_team


def _create_mock_scrim(*team_names: str) -> Scrim:
    mock_scrim = MagicMock()
    mock_scrim.teams = []
    for team_name in team_names:
        mock_team = MagicMock()
        mock_team.name = team_name
        mock_scrim.teams.append(mock_team)
    return mock_scrim


class TestLookingForPlayersState(UnittestBase):

    def setUp(self) -> None:
        self.state = BasicStateImplementation()

    def test_build_team_participants_given_a_team_has_members_then_members_listed_with_nickname_mentions(self):
        mock_team = _create_mock_team(1, 2, 3)
        member_string = self.state.build_team_participants(mock_team)
        self.assertEqual(f"<@!1>{os.linesep}<@!2>{os.linesep}<@!3>", member_string)

    def test_build_team_participants_given_a_team_with_no_members_then_empty_returned(self):
        mock_team = _create_mock_team()
        member_string = self.state.build_team_participants(mock_team)
        self.assertEqual("_empty_", member_string)

    def test_get_setup_teams_given_all_setup_teams_and_two_game_teams_then_only_setup_teams_returned(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")
        setup_teams = self.state.get_setup_teams(mock_scrim)
        self._assert_teams_returned(setup_teams, PARTICIPANTS, SPECTATORS, QUEUE)

    def test_get_setup_teams_given_no_queue_then_only_participants_and_spectators_returned(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, "Team 1", "Team 2")
        setup_teams = self.state.get_setup_teams(mock_scrim)
        self._assert_teams_returned(setup_teams, PARTICIPANTS, SPECTATORS)

    def test_get_game_teams_given_no_game_teams_then_empty_list_returned(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, QUEUE)
        setup_teams = self.state.get_game_teams(mock_scrim)
        self._assert_teams_returned(setup_teams)

    def test_get_game_teams_given_game_teams_exist_then_all_game_teams_returned(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")
        setup_teams = self.state.get_game_teams(mock_scrim)
        self._assert_teams_returned(setup_teams, "Team 1", "Team 2")

    def _assert_teams_returned(self, setup_teams, *team_names: str):
        self.assertEqual(len(team_names), len(setup_teams))
        for expected_team_name, actual_team in zip(team_names, setup_teams):
            self.assertEqual(expected_team_name, actual_team.name)
