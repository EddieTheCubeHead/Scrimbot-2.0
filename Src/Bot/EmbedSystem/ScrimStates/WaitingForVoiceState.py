__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class WaitingForVoiceState(StartedState):

    @property
    def description(self) -> str:
        return "waiting for players to join voice channel"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        return f"Starting {teams_manager.game.name} scrim. Waiting for all players to join voice chat..."

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        return "Scrim will start automatically when all players are in voice chat"
