__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from discord import Message
from hintedi import HinteDI

from Src.Bot.Cogs.Helpers.ScrimTeamOperationService import ScrimTeamOperationService
from Src.Bot.Converters.Convertable import Convertable
from Src.Bot.Converters.TeamCreationStrategyConverter import TeamCreationStrategyConverter
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.Logic.ScrimManager import ScrimManager
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class TeamCreationStrategy(ABC, Convertable):

    @HinteDI.inject
    def __init__(self, team_service: ScrimTeamOperationService):
        self._team_service = team_service

    @abstractmethod
    def _create_teams_hook(self, scrim: Scrim):  # pragma: no cover
        pass

    async def create_teams(self, scrim: Scrim, message: Message):
        self._team_service.clear_teams()
        self._create_teams_hook(scrim)
        await self._set_reactions_hook(scrim, message)

    async def _set_reactions_hook(self, scrim: Scrim, message: Message):
        await message.clear_reactions()

    @classmethod
    @HinteDI.inject
    def set_converter(cls, converter: TeamCreationStrategyConverter):  # pragma: no cover
        super().set_converter(converter)
