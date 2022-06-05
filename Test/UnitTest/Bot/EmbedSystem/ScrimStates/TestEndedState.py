__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.EmbedSystem.ScrimStates.EndedState import EndedState
from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Utils.TestBases.StateUnittest import StateUnittest


class TestEndedState(StateUnittest):

    def test_build_description_when_winner_is_none_then_only_scrim_ended_info_returned(self):
        state = EndedState()
        self.teams_manager.winner = None
        self.assertEqual("Scrim has ended", state.build_description(self.teams_manager))

    def test_build_description_when_winner_exists_then_scrim_ended_and_winner_info_returned(self):
        state = EndedState()
        self.teams_manager.winner = "Team 1"
        self.assertEqual("Scrim has ended with Team 1 being victorious. Congratulations!",
                         state.build_description(self.teams_manager))

    def test_build_fields_when_called_then_returns_identical_to_started_state(self):
        self.add_team_1(*list(range(5)))
        self.add_team_2(*list(range(5, 9)))
        state = EndedState()
        started_state = StartedState()
        expected_fields = started_state.build_fields(self.teams_manager)
        actual_fields = state.build_fields(self.teams_manager)
        self.assertEqual(expected_fields, actual_fields)

    def test_build_footer_when_called_then_returns_gg_wp(self):
        state = EndedState()
        self.assertEqual("gg wp!", state.build_footer(self.teams_manager))
