__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Union

from discord.ext import commands

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


ScrimResult = list[tuple[Team, ...]]


def _name_conversion(ctx: ScrimContext, argument: str) -> ScrimResult:
    results = []
    for team in ctx.scrim.teams_manager.get_game_teams():
        _insert_result(team.name, argument, team, results)
    return results


def _digit_conversion(ctx: ScrimContext, argument: int) -> ScrimResult:
    results = []
    for number, team in enumerate(ctx.scrim.teams_manager.get_game_teams(), 1):
        _insert_result(number, argument, team, results)
    return results


def _insert_result(team_argument: Union[str, int], result_argument: Union[str, int], team: Team,
                   results: list[tuple[Team]]):
    if team_argument == result_argument:
        results.insert(0, (team,))
    else:
        results.append((team,))


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
        return results
