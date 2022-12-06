__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import unittest

from Bot.DataClasses.Scrim import ScrimState
from Bot.EmbedSystem.ScrimStates.LookingForPlayersState import LookingForPlayersState
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Test.Utils.TestBases.StateUnittest import StateUnittest


class TestLookingForPlayersState(StateUnittest):

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_concrete_dependency(LookingForPlayersState, ScrimStateBase, ScrimState.LFP)

    def test_build_description_given_not_enough_players_then_remaining_players_returned(self):
        state = LookingForPlayersState()
        for player_count in range(10):
            with self.subTest(f"Test LFP needed players description ({10 - player_count} required)"):
                self.participants.team.members.clear()
                self.add_participants(*range(player_count))
                expected_description = f"Looking for players, {10 - player_count} more required."
                self.assertEqual(expected_description, state.build_description(self.scrim))

    def test_build_description_given_game_full_then_locking_info_returned(self):
        state = LookingForPlayersState()
        self.add_participants(*range(10))
        expected_description = "All players present. Send command 'lock' to start team selection."
        self.assertEqual(expected_description, state.build_description(self.scrim))

    def test_build_description_given_min_playercount_but_not_max_then_locking_info_and_room_left_returned(self):
        self.mock_game = self.create_mock_game("Test 2", 2, 5, 8)
        self.scrim.game = self.mock_game
        state = LookingForPlayersState()
        self.add_participants(*range(10))
        expected_description = "Enough players present. Room for 6 more. Send command 'lock' to start team selection."
        self.assertEqual(expected_description, state.build_description(self.scrim))

    def test_build_description_given_different_min_and_max_players_and_game_full_then_locking_info_returned(self):
        self.mock_game = self.create_mock_game("Test 2", 2, 5, 8)
        self.scrim.game = self.mock_game
        state = LookingForPlayersState()
        self.add_participants(*range(16))
        expected_description = "All players present. Send command 'lock' to start team selection."
        self.assertEqual(expected_description, state.build_description(self.scrim))

    def test_build_fields_given_empty_teams_then_empty_fields_returned(self):
        state = LookingForPlayersState()
        actual_fields = state.build_fields(self.scrim)
        self.assertEqual([(ScrimTeamsManager.PARTICIPANTS, "_empty_", True),
                          (ScrimTeamsManager.SPECTATORS, "_empty_", True)], actual_fields)

    def test_build_fields_given_participants_less_or_equal_to_max_players_then_participants_field_filled(self):
        state = LookingForPlayersState()
        for player_count in range(2, 11):
            with self.subTest(f"Test LFP build participants field ({player_count - 1} participants)"):
                self.participants.team.members.clear()
                participants = list(range(1, player_count))
                self.add_participants(*participants)
                expected_participants = "<@!" + f">{os.linesep}<@!".join([str(num) for num in participants]) + ">"
                actual_fields = state.build_fields(self.scrim)
                self.assertEqual([(ScrimTeamsManager.PARTICIPANTS, expected_participants, True),
                                  (ScrimTeamsManager.SPECTATORS, "_empty_", True)], actual_fields)

    def test_build_fields_given_any_number_of_spectators_then_spectators_field_filled(self):
        state = LookingForPlayersState()
        for spectator_count in range(2, 21):
            with self.subTest(f"Test LFP build spectators field ({spectator_count - 1} spectators)"):
                self.spectators.team.members.clear()
                spectators = list(range(1, spectator_count))
                self.add_spectators(*spectators)
                expected_spectators = "<@!" + f">{os.linesep}<@!".join([str(num) for num in spectators]) + ">"
                actual_fields = state.build_fields(self.scrim)
                self.assertEqual([(ScrimTeamsManager.PARTICIPANTS, "_empty_", True),
                                  (ScrimTeamsManager.SPECTATORS, expected_spectators, True)], actual_fields)

    def test_build_fields_given_more_participants_than_fits_then_queue_filled(self):
        state = LookingForPlayersState()
        for player_count in range(2, 6):
            with self.subTest(f"Test LFP build participants field with queue ({player_count - 1} participants)"):
                self.participants.team.members.clear()
                self.queue.team.members.clear()
                participants = list(range(1, 11))
                queue = list(range(1, player_count))
                self.add_participants(*participants)
                self.add_queued(*queue)
                expected_participants = "<@!" + f">{os.linesep}<@!".join([str(num) for num in participants]) + ">"
                expected_queue = "<@!" + f">{os.linesep}<@!".join([str(num) for num in queue]) + ">"
                actual_fields = state.build_fields(self.scrim)
                self.assertEqual([(ScrimTeamsManager.PARTICIPANTS, expected_participants, True),
                                  (ScrimTeamsManager.SPECTATORS, "_empty_", True),
                                  (ScrimTeamsManager.QUEUE, expected_queue, True)], actual_fields)

    def test_build_footer_given_not_full_then_joining_info_returned(self):
        state = LookingForPlayersState()
        for player_count in range(10):
            with self.subTest(f"Test LFP joining info footer ({player_count} players present)"):
                self.participants.team.members.clear()
                self.add_participants(*range(player_count))
                expected_footer = "To join players react 🎮 To join spectators react 👁"
                self.assertEqual(expected_footer, state.build_footer(self.scrim))

    def test_build_footer_given_game_full_then_joining_and_locking_info_returned(self):
        state = LookingForPlayersState()
        self.participants.team.members.clear()
        self.add_participants(*range(10))
        expected_footer = "To join players react 🎮 To join spectators react 👁 To lock the teams send " \
                          "command 'lock'"
        self.assertEqual(expected_footer, state.build_footer(self.scrim))
