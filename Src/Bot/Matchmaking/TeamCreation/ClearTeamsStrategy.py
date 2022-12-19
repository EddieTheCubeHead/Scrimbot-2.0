__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Message

from Src.Bot.Converters.TeamCreationStrategyConverter import TeamCreationStrategyConverter
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.Logic import ScrimManager
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Src.Bot.Matchmaking.TeamCreation.TeamCreationStrategy import TeamCreationStrategy


@TeamCreationStrategyConverter.register("clear")
class ClearTeamsStrategy(TeamCreationStrategy):

    def _create_teams_hook(self, teams_manager: ScrimTeamsManager):
        pass

    async def _set_reactions_hook(self, scrim: Scrim, message: Message):
        await message.clear_reactions()
        for team in range(1, scrim.game.team_count + 1):
            await message.add_reaction(emoji=f"{team}\u20E3")
