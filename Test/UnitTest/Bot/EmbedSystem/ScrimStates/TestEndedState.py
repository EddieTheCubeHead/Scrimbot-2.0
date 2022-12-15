__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Src.Bot.Converters.ScrimResultConverter import ScrimResult
from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team
from Src.Bot.EmbedSystem.ScrimStates.EndedState import EndedState
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Utils.TestBases.StateUnittest import StateUnittest


def _create_winners(scrim: Scrim, *winner_names: str) -> ScrimResult:
    for team in [participant_team.team for participant_team in scrim.teams]:
        if team.name in winner_names:
            team.winner = True


class TestEndedState(StateUnittest):

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_concrete_dependency(EndedState, ScrimStateBase, ScrimState.ENDED)

    def test_build_description_when_winner_is_empty_list_then_only_scrim_ended_info_returned(self):
        state = EndedState()
        _create_winners(self.scrim)
        self.assertEqual("Scrim has ended", state.build_description(self.scrim))

    def test_build_description_when_winner_list_first_tuple_has_multiple_teams_then_tie_returned_with_team_names(self):
        state = EndedState()
        _create_winners(self.scrim, "Team 1", "Team 2")
        self.assertEqual("Scrim has ended in a tie between Team 1 and Team 2",
                         state.build_description(self.scrim))

    def test_build_description_when_winner_exists_then_scrim_ended_and_winner_info_returned(self):
        state = EndedState()
        _create_winners(self.scrim, "Team 1")
        self.assertEqual("Scrim has ended with Team 1 being victorious. Congratulations!",
                         state.build_description(self.scrim))

    def test_build_fields_when_called_then_returns_identical_to_started_state(self):
        self.add_team_1(*list(range(5)))
        self.add_team_2(*list(range(5, 9)))
        state = EndedState()
        started_state = StartedState()
        expected_fields = started_state.build_fields(self.scrim)
        actual_fields = state.build_fields(self.scrim)
        self.assertEqual(expected_fields, actual_fields)

    def test_build_footer_when_called_then_returns_gg_wp(self):
        state = EndedState()
        self.assertEqual("gg wp!", state.build_footer(self.scrim))
