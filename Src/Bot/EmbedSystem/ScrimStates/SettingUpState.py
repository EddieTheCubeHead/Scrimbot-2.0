__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.SETTING_UP)
class SettingUpState(ScrimStateBase):
    @property
    def description(self) -> str:
        return "setting up a scrim"

    @staticmethod
    def build_description(scrim: Scrim) -> str:
        return "Setting up a scrim..."

    @staticmethod
    def build_fields(scrim: Scrim) -> list[(str, str, bool)]:
        return []

    @staticmethod
    def build_footer(scrim: Scrim) -> str:
        return "This should not take too long."
