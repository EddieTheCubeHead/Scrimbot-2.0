__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


def _create_result_scrim(ctx, results: ScrimResult):
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


class ResultHandler:

    @BotDependencyInjector.inject
    def __init__(self, connection: ScrimConnection):
        self._connection = connection

    def save_result(self, ctx, result: ScrimResult):
        result_scrim = _create_result_scrim(ctx, result)
        self._connection.add_scrim(result_scrim)
