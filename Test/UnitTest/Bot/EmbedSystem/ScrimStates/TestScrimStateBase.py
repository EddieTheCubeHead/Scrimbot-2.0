__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
from unittest.mock import MagicMock

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team, PARTICIPANTS, SPECTATORS, QUEUE
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.StateUnittest import UnittestBase


class BasicStateImplementation(ScrimStateBase):

    def __init__(self):
        self.mock_method = MagicMock()

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return [ScrimState.LOCKED]

    def build_description(self, scrim: Scrim) -> str:
        pass

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        pass

    def build_footer(self, scrim: Scrim) -> str:
        pass

    @property
    def description(self) -> str:
        return 'description'

    def transition_hook(self, scrim: Scrim, new_state: ScrimState):
        self.mock_method(scrim, new_state)


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
        mock_participant_team = MagicMock()
        mock_team = MagicMock()
        mock_team.name = team_name
        mock_participant_team.team = mock_team
        mock_scrim.teams.append(mock_participant_team)
    return mock_scrim


class TestScrimStateBase(UnittestBase):

    def setUp(self) -> None:
        self.state = BasicStateImplementation()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_abstract_base_dependency(ScrimStateBase)

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

    def test_transition_when_state_in_valid_transitions_and_assert_transition_runs_then_transitioned(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")
        mock_scrim.state = ScrimState.LFP
        mock_state_provider = MagicMock()
        mock_locked_state = MagicMock()
        mock_state_provider.resolve_from_key.return_value = mock_locked_state
        new_state = self.state.transition(mock_scrim, ScrimState.LOCKED, mock_state_provider)
        self.assertEqual(ScrimState.LOCKED, mock_scrim.state)
        self.assertEqual(mock_locked_state, new_state)

    def test_transition_when_state_not_in_valid_transitions_then_throws(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")
        mock_scrim.state = ScrimState.LFP
        mock_state_provider = MagicMock()
        mock_new_state = MagicMock()
        mock_state_provider.resolve_from_key.return_value = mock_new_state
        for state in (ScrimState.STARTED, ScrimState.TERMINATED, ScrimState.SETTING_UP, ScrimState.VOICE_WAIT,
                      ScrimState.ENDED, ScrimState.CAPS_PREP, ScrimState.CAPS):
            with self.subTest(f"State transition should fail if target state is not valid ({state})"):
                expected_exception = BotInvalidStateChangeException(self.state, mock_new_state)
                self._assert_raises_correct_exception(expected_exception, self.state.transition, MagicMock(), state,
                                                      mock_state_provider)

    def test_transition_when_state_transition_performed_then_transition_hook_ran(self):
        mock_scrim = _create_mock_scrim(PARTICIPANTS, SPECTATORS, QUEUE, "Team 1", "Team 2")
        mock_scrim.state = ScrimState.LFP
        mock_state_provider = MagicMock()
        mock_locked_state = MagicMock()
        mock_state_provider.resolve_from_key.return_value = mock_locked_state
        self.state.transition(mock_scrim, ScrimState.LOCKED, mock_state_provider)
        self.state.mock_method.assert_called_with(mock_scrim, ScrimState.LOCKED)

    def _assert_teams_returned(self, setup_teams, *team_names: str):
        self.assertEqual(len(team_names), len(setup_teams))
        for expected_team_name, actual_team in zip(team_names, setup_teams):
            self.assertEqual(expected_team_name, actual_team.name)
