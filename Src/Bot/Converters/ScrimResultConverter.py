__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


def _name_conversion(ctx: ScrimContext, argument: str) -> list[tuple]:
    results = []
    for team in ctx.scrim.teams_manager.get_game_teams():
        if team.name == argument:
            results.insert(0, (team,))
        else:
            results.append((team,))
    return results


def _digit_conversion(ctx: ScrimContext, argument: int) -> list[tuple]:
    results = []
    for number, team in enumerate(ctx.scrim.teams_manager.get_game_teams(), 1):
        if number == argument:
            results.insert(0, (team,))
        else:
            results.append((team,))
    return results


def _create_result_scrim(ctx, results):
    result_scrim = Scrim(ctx.scrim)
    placement = 1
    for team_tuple in results:
        placement_increment = 0
        for team in team_tuple:
            placement_increment += 1
            participant_team = ParticipantTeam(placement)
            participant_team.team = team
            result_scrim.teams.append(participant_team)
            result_scrim.teams[-1].placement = placement
        placement += placement_increment
    return result_scrim


class ScrimResultConverter(ConverterBase):

    connection: ScrimConnection

    @BotDependencyInjector.inject
    def __init__(self, scrim_connection: ScrimConnection):
        super().__init__(scrim_connection)

    async def convert(self, ctx: ScrimContext, argument: str):
        if argument.isnumeric():
            results = _digit_conversion(ctx, int(argument))
        else:
            results = _name_conversion(ctx, argument)
        result_scrim = _create_result_scrim(ctx, results)
        self.connection.add_scrim(result_scrim)
        return results[0][0].name
