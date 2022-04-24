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


def _name_conversion(ctx: ScrimContext, argument: str) -> list[tuple[Team]]:
    results = []
    for team in ctx.scrim.teams_manager.get_game_teams():
        _insert_result(team.name, argument, team, results)
    return results


def _digit_conversion(ctx: ScrimContext, argument: int) -> list[tuple[Team]]:
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


def _create_result_scrim(ctx, results):
    result_scrim = Scrim(ctx.scrim)
    placement = 1
    for team_tuple in results:
        placement += _create_placement_teams(placement, result_scrim, team_tuple)
    return result_scrim


def _create_placement_teams(placement: int, result_scrim: Scrim, team_tuple: tuple[Team]) -> int:
    placement_increment = 0
    for team in team_tuple:
        placement_increment += 1
        result_scrim.teams.append(_create_placement_team(placement, team))
    return placement_increment


def _create_placement_team(placement: int, team: Team) -> ParticipantTeam:
    participant_team = ParticipantTeam(placement)
    participant_team.team = team
    return participant_team


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
