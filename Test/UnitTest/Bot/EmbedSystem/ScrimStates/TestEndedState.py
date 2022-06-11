__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.DataClasses.Team import Team
from Bot.EmbedSystem.ScrimStates.EndedState import EndedState
from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Utils.TestBases.StateUnittest import StateUnittest


def _create_results(*teams: tuple[str, ...]) -> ScrimResult:
    results = []
    for placement in teams:
        placements = []
        for team in placement:
            mock_team = MagicMock()
            mock_team.name = team
            placements.append(mock_team)
        results.append(tuple(placements))
    return results


class TestEndedState(StateUnittest):

    def test_build_description_when_winner_is_empty_list_then_only_scrim_ended_info_returned(self):
        state = EndedState()
        self.teams_manager.result = _create_results()
        self.assertEqual("Scrim has ended", state.build_description(self.teams_manager))

    def test_build_description_when_winner_list_first_tuple_has_multiple_teams_then_tie_returned_with_team_names(self):
        state = EndedState()
        self.teams_manager.result = _create_results(("Team 1", "Team 2"))
        self.assertEqual("Scrim has ended in a tie between Team 1 and Team 2",
                         state.build_description(self.teams_manager))

    def test_build_description_when_winner_exists_then_scrim_ended_and_winner_info_returned(self):
        state = EndedState()
        self.teams_manager.result = _create_results(("Team 1",), ("Team 2",))
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
