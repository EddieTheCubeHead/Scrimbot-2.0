__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from hintedi import HinteDI

from Bot.Converters.Convertable import Convertable
from Bot.Converters.TeamCreationStrategyConverter import TeamCreationStrategyConverter
from Bot.Logic.ScrimManager import ScrimManager
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class TeamCreationStrategy(ABC, Convertable):

    @abstractmethod
    def _create_teams_hook(self, teams_manager: ScrimTeamsManager):  # pragma: no cover
        pass

    async def create_teams(self, scrim_manager: ScrimManager):
        scrim_manager.teams_manager.clear_teams()
        self._create_teams_hook(scrim_manager.teams_manager)
        await self._set_reactions_hook(scrim_manager)

    async def _set_reactions_hook(self, scrim_manager: ScrimManager):
        await scrim_manager.message.clear_reactions()

    @classmethod
    @HinteDI.inject
    def set_converter(cls, converter: TeamCreationStrategyConverter):  # pragma: no cover
        super().set_converter(converter)
