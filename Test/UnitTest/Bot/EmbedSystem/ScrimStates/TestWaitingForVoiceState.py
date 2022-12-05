__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import unittest

from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Bot.EmbedSystem.ScrimStates.WaitingForVoiceState import WaitingForVoiceState
from Utils.TestBases.StateUnittest import StateUnittest


class TestWaitingForVoiceState(StateUnittest):

    def test_get_description_when_called_then_returns_waiting_info(self):
        state = WaitingForVoiceState()
        self.assertEqual(f"Starting {self.mock_game.name} scrim. Waiting for all players to join voice chat...",
                         state.build_description(self.scrim))

    def test_build_fields_when_called_then_returns_identical_to_started_state(self):
        self.add_team_1(*list(range(5)))
        self.add_team_2(*list(range(5, 9)))
        state = WaitingForVoiceState()
        started_state = StartedState()
        expected_fields = started_state.build_fields(self.scrim)
        actual_fields = state.build_fields(self.scrim)
        self.assertEqual(expected_fields, actual_fields)

    def test_build_footer_when_called_then_returns_automatic_starting_info(self):
        state = WaitingForVoiceState()
        self.assertEqual("Scrim will start automatically when all players are in voice chat",
                         state.build_footer(self.scrim))
