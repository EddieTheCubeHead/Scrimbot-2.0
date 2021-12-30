__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os

from Bot.EmbedSystem.ScrimStates.LockedState import LockedState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Utils.TestBases.StateUnittest import StateUnittest


class TestLockedState(StateUnittest):

    _divider = "----------------------------------------------"

    def test_build_description_given_unassigned_left_then_joining_info_returned(self):
        expected_description = "Players locked. Use reactions for manual team selection or the command 'teams " \
                               "_random/balanced/balancedrandom/pickup_' to define teams."
        state = LockedState()
        for player_count in range(1, 11):
            with self.subTest(f"Test locked joining description ({player_count} unassigned)"):
                self.participants.members.clear()
                self.add_participants(*range(player_count))
                self.assertEqual(expected_description, state.build_description(self.teams_manager))

    def test_build_fields_given_all_unassigned_no_spectators_then_teams_empty_and_unassigned_shown_correctly(self):
        state = LockedState()
        self.add_participants(*range(1, 11))
        expected_participants = "<@" + f">{os.linesep}<@".join([str(num) for num in range(1, 11)]) + ">"
        actual_fields = state.build_fields(self.teams_manager)
        self.assertEqual([("Unassigned", expected_participants, True),
                          (ScrimTeamsManager.SPECTATORS, "_empty_", True),
                          (self._divider, self._divider, False),
                          ("Team 1 _(5 more needed)_", "_empty_", True),
                          ("Team 2 _(5 more needed)_", "_empty_", True)], actual_fields)

    def test_build_footer_given_unassigned_left_then_joining_info_returned(self):
        expected_footer = "React 1️⃣ to join Team 1 or 2️⃣ to join Team 2"
        state = LockedState()
        for player_count in range(1, 11):
            with self.subTest(f"Test locked joining footer ({player_count} unassigned)"):
                self.participants.members.clear()
                self.add_participants(*range(player_count))
                self.assertEqual(expected_footer, state.build_footer(self.teams_manager))
