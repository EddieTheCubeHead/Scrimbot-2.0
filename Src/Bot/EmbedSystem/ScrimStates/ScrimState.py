__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class ScrimState(ABC):

    @property
    @abstractmethod
    def description(self) -> str:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:  # pragma: no cover
        pass
