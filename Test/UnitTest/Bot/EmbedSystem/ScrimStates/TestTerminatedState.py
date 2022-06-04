__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.EmbedSystem.ScrimStates.TerminatedState import TerminatedState
from Utils.TestBases.StateUnittest import StateUnittest


class TestTerminatedState(StateUnittest):

    def test_build_description_when_manager_has_terminator_then_terminator_given(self):
        state = TerminatedState()
        mock_author = MagicMock()
        mock_author.id = self.id_builder.generate_viable_id()
        self.teams_manager.terminator = mock_author.id
        self.assertEqual(f"Scrim terminated manually by <@{mock_author.id}>",
                         state.build_description(self.teams_manager))

    def test_build_description_when_manager_does_not_have_terminator_then_automatical_termination_message_given(self):
        state = TerminatedState()
        self.teams_manager.terminator = None
        self.assertEqual("Scrim terminated automatically after inactivity", state.build_description(self.teams_manager))

    def test_build_fields_when_called_then_returns_empty_list(self):
        actual = TerminatedState().build_fields(self.teams_manager)
        self.assertEqual(list, type(actual))
        self.assertEqual(0, len(actual))

    def test_build_footer_when_called_then_returns_f(self):
        self.assertEqual("f", TerminatedState().build_footer(self.teams_manager))
