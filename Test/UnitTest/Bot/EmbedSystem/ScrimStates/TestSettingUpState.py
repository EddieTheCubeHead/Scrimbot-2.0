__version__ = "0.2"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Src.Bot.DataClasses.Scrim import ScrimState
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.EmbedSystem.ScrimStates.SettingUpState import SettingUpState
from Utils.TestBases.StateUnittest import StateUnittest


class TestStartedState(StateUnittest):

    def setUp(self) -> None:
        self.state = SettingUpState()
        self.scrim = MagicMock()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_concrete_dependency(SettingUpState, ScrimStateBase, ScrimState.SETTING_UP)

    def test_description_returns_setting_up(self):
        self.assertEqual("setting up a scrim", self.state.description)

    def test_build_description_returns_setting_up(self):
        self.assertEqual("Setting up...", self.state.build_description(self.scrim))

    def test_build_fields_returns_empty_array(self):
        self.assertEqual([], self.state.build_fields(self.scrim))

    def test_build_footer_returns_should_not_take_long(self):
        self.assertEqual("This should not take too long.", self.state.build_footer(self.scrim))
