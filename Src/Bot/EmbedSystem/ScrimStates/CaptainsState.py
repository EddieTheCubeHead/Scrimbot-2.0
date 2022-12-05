__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.Scrim import Scrim
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState


class CaptainsState(ScrimState):

    @property
    def description(self) -> str:
        return "letting captains pick players"

    @staticmethod
    def build_description(scrim: Scrim) -> str:
        pass

    @staticmethod
    def build_fields(scrim: Scrim) -> list[(str, str, bool)]:
        pass

    @staticmethod
    def build_footer(scrim: Scrim) -> str:
        pass
