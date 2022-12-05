__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import ScrimState
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.VOICE_WAIT)
class WaitingForVoiceState(StartedState):

    @property
    def description(self) -> str:
        return "waiting for players to join voice channel"

    @staticmethod
    def build_description(scrim: ScrimTeamsManager) -> str:
        return f"Starting {scrim.game.name} scrim. Waiting for all players to join voice chat..."

    @staticmethod
    def build_footer(scrim: ScrimTeamsManager) -> str:
        return "Scrim will start automatically when all players are in voice chat"
