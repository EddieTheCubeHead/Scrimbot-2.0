__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import unittest
from unittest.mock import MagicMock

from Bot.DataClasses.Scrim import ScrimState
from Bot.EmbedSystem.ScrimStates.LockedState import LockedState
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.StateUnittest import StateUnittest


class TestLockedState(StateUnittest):

    _divider = "----------------------------------------------"

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_concrete_dependency(LockedState, ScrimStateBase, ScrimState.LOCKED)

    def test_build_description_given_unassigned_left_then_joining_info_returned(self):
        expected_description = "Players locked. Use reactions for manual team selection or the command 'teams " \
                               "_random/balanced/balancedrandom/pickup_' to define teams."
        state = LockedState()
        self.scrim.has_participants = True
        self.scrim.has_full_teams = False
        self.assertEqual(expected_description, state.build_description(self.scrim))

    def test_build_description_given_no_unassigned_left_and_all_teams_have_min_players_then_start_info_shown(self):
        expected_description = "Teams full, use the command 'start' to start the scrim or 'teams clear' to clear teams"
        state = LockedState()
        self.scrim.has_participants = False
        self.scrim.has_full_teams = True
        actual_description = state.build_description(self.scrim)
        self.assertEqual(expected_description, actual_description)

    def test_build_description_given_no_unassigned_left_but_not_all_teams_have_min_players_then_start_info_shown(self):
        expected_description = "No unassigned players left but all teams are not full! Please rebalance the teams " \
                               "with reactions or use the command 'teams _random/balanced/balancedrandom/pickup_'."
        state = LockedState()
        self.scrim.has_participants = False
        self.scrim.has_full_teams = False
        actual_description = state.build_description(self.scrim)
        self.assertEqual(expected_description, actual_description)

    def test_build_fields_given_all_unassigned_no_spectators_then_teams_empty_and_unassigned_shown_correctly(self):
        state = LockedState()
        self.add_participants(*range(1, 11))
        expected_participants = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(1, 11)]) + ">"
        actual_fields = state.build_fields(self.scrim)
        self.assertEqual([("Unassigned", expected_participants, True),
                          (ScrimTeamsManager.SPECTATORS, "_empty_", True),
                          (self._divider, self._divider, False),
                          ("Team 1 _(5 more needed)_", "_empty_", True),
                          ("Team 2 _(5 more needed)_", "_empty_", True)], actual_fields)

    def test_build_fields_given_team_has_members_less_than_min_no_spectators_then_members_shown_correctly(self):
        state = LockedState()
        for num in range(1, 5):
            with self.subTest(f"Displaying team members in team creation stage ({num} members)"):
                self.participants.team.members.clear()
                self.team_1.team.members.clear()
                self.add_participants(*range(6, 16 - num))
                self.add_team_1(*range(1, num + 1))
                expected_participants = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(6, 16 - num)]) + ">"
                expected_team_members = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(1, num + 1)]) + ">"
                actual_fields = state.build_fields(self.scrim)
                self.assertEqual([("Unassigned", expected_participants, True),
                                  (ScrimTeamsManager.SPECTATORS, "_empty_", True),
                                  (self._divider, self._divider, False),
                                  (f"Team 1 _({5 - num} more needed)_", expected_team_members, True),
                                  ("Team 2 _(5 more needed)_", "_empty_", True)], actual_fields)

    def test_build_fields_given_team_full_enough_but_room_left_then_members_shown_correctly(self):
        state = LockedState()
        self.team_1.team.max_size = 8
        self.team_2.team.max_size = 8
        self.add_participants(*range(6, 11))
        self.add_team_1(*range(1, 6))
        expected_participants = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(6, 11)]) + ">"
        expected_team_1_members = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(1, 6)]) + ">"
        actual_fields = state.build_fields(self.scrim)
        self.assertEqual([("Unassigned", expected_participants, True),
                          (ScrimTeamsManager.SPECTATORS, "_empty_", True),
                          (self._divider, self._divider, False),
                          ("Team 1 _(enough players: room for 3 more)_", expected_team_1_members, True),
                          ("Team 2 _(5 more needed)_", "_empty_", True)], actual_fields)

    def test_build_fields_given_team_full_then_members_shown_correctly(self):
        state = LockedState()
        self.add_participants(*range(6, 11))
        self.add_team_1(*range(1, 6))
        expected_participants = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(6, 11)]) + ">"
        expected_team_1_members = "<@!" + f">{os.linesep}<@!".join([str(num) for num in range(1, 6)]) + ">"
        actual_fields = state.build_fields(self.scrim)
        self.assertEqual([("Unassigned", expected_participants, True),
                          (ScrimTeamsManager.SPECTATORS, "_empty_", True),
                          (self._divider, self._divider, False),
                          ("Team 1 _(full)_", expected_team_1_members, True),
                          ("Team 2 _(5 more needed)_", "_empty_", True)], actual_fields)

    def test_build_footer_given_unassigned_left_then_joining_info_returned(self):
        self.add_participants(1)
        expected_footer = "React 1️⃣ to join Team 1 or 2️⃣ to join Team 2"
        state = LockedState()
        self.assertEqual(expected_footer, state.build_footer(self.scrim))

    def test_build_footer_teams_full_then_starting_info_returned(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 10))
        expected_footer = "Send command 'start' to start the scrim or send command 'teams clear' to clear teams"
        state = LockedState()
        self.scrim.has_participants = False
        self.scrim.has_full_teams = True
        self.assertEqual(expected_footer, state.build_footer(self.scrim))

    def test_transition_given_teams_full_when_moving_to_started_state_then_state_transition_successful(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 10))
        state = LockedState()
        mock_state_provider = MagicMock()
        new_state_mock = MagicMock()
        mock_state_provider.resolve_from_key.return_value = new_state_mock
        new_state = state.transition(self.scrim, ScrimState.STARTED, mock_state_provider)
        self.assertEqual(new_state_mock, new_state)
        self.assertEqual(self.scrim.state, ScrimState.STARTED)

    def test_transition_given_participants_left_when_moving_to_started_state_then_exception_raised(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 10))
        self.add_participants(10, 11)
        state = LockedState()
        mock_state_provider = MagicMock()
        new_state_mock = MagicMock()
        mock_state_provider.resolve_from_key.return_value = new_state_mock
        expected_exception = BotBaseRespondToContextException(
            "Could not start the scrim. All participants are not in a team.", send_help=False)
        self._assert_raises_correct_exception(expected_exception, state.transition, self.scrim, ScrimState.STARTED,
                                              mock_state_provider)

    def test_transition_given_teams_not_full_when_moving_to_started_state_then_exception_raised(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 9))
        state = LockedState()
        mock_state_provider = MagicMock()
        new_state_mock = MagicMock()
        mock_state_provider.resolve_from_key.return_value = new_state_mock
        expected_exception = BotBaseRespondToContextException(
            "Could not start the scrim. Some teams lack the minimum number of players required.", send_help=False)
        self._assert_raises_correct_exception(expected_exception, state.transition, self.scrim, ScrimState.STARTED,
                                              mock_state_provider)

    def test_transition_given_teams_full_when_moving_to_voice_wait_state_then_state_transition_successful(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 10))
        state = LockedState()
        mock_state_provider = MagicMock()
        new_state_mock = MagicMock()
        mock_state_provider.resolve_from_key.return_value = new_state_mock
        new_state = state.transition(self.scrim, ScrimState.VOICE_WAIT, mock_state_provider)
        self.assertEqual(new_state_mock, new_state)
        self.assertEqual(self.scrim.state, ScrimState.VOICE_WAIT)

    def test_transition_given_participants_left_when_moving_to_voice_wait_state_then_exception_raised(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 10))
        self.add_participants(10, 11)
        state = LockedState()
        mock_state_provider = MagicMock()
        new_state_mock = MagicMock()
        mock_state_provider.resolve_from_key.return_value = new_state_mock
        expected_exception = BotBaseRespondToContextException(
            "Could not start the scrim. All participants are not in a team.", send_help=False)
        self._assert_raises_correct_exception(expected_exception, state.transition, self.scrim, ScrimState.VOICE_WAIT,
                                              mock_state_provider)

    def test_transition_given_teams_not_full_when_moving_to_voice_wait_state_then_exception_raised(self):
        self.add_team_1(*range(5))
        self.add_team_2(*range(5, 9))
        state = LockedState()
        mock_state_provider = MagicMock()
        new_state_mock = MagicMock()
        mock_state_provider.resolve_from_key.return_value = new_state_mock
        expected_exception = BotBaseRespondToContextException(
            "Could not start the scrim. Some teams lack the minimum number of players required.", send_help=False)
        self._assert_raises_correct_exception(expected_exception, state.transition, self.scrim, ScrimState.VOICE_WAIT,
                                              mock_state_provider)
