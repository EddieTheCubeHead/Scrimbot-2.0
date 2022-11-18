__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Union

from hintedi import HinteDI

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.Team import Team
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


ScrimResult = list[tuple[Team, ...]] | None


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

    @HinteDI.inject
    def __init__(self, scrim_connection: ScrimConnection):
        super().__init__(scrim_connection)

    async def convert(self, ctx: ScrimContext, argument: str):
        self._assert_correct_team_amount(argument, ctx)
        if argument.isnumeric():
            results = _digit_conversion(ctx, int(argument))
        else:
            results = _name_conversion(ctx, argument)
        return results

    @staticmethod
    def _assert_correct_team_amount(argument, ctx):
        if len(ctx.scrim.teams_manager.get_game_teams()) > 2:
            reason = "recording results for scrims with more than two teams is not currently supported"
            raise BotConversionFailureException("scrim result", argument, reason=reason)
        elif len(ctx.scrim.teams_manager.get_game_teams()) == 1:
            reason = "recording results for scrims with only one team is not currently supported"
            raise BotConversionFailureException("scrim result", argument, reason=reason)
