__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.SETTING_UP)
class SettingUpState(ScrimStateBase):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return []

    @property
    def description(self) -> str:
        return "setting up a scrim"

    def build_description(self, scrim: Scrim) -> str:
        return "Setting up..."

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        return []

    def build_footer(self, scrim: Scrim) -> str:
        return "This should not take too long."
