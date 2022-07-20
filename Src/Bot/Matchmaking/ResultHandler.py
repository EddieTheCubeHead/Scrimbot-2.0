__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.Converters.UserRatingConverter import UserRatingConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.DataClasses.UserScrimResult import Result
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


class ResultHandler:

    @BotDependencyInjector.inject
    def __init__(self, connection: ScrimConnection, converter: UserRatingConverter):
        self._connection = connection
        self._converter = converter

    def save_result(self, ctx: ScrimContext, result: ScrimResult):
        result_scrim = self._create_result_scrim(ctx, result)
        self._connection.add_scrim(result_scrim)
        self._update_user_ratings(ctx, result)

    def _create_result_scrim(self, ctx: ScrimContext, results: ScrimResult):
        result_scrim = Scrim(ctx.scrim)
        if results is not None:
            self._set_placements_from_results(result_scrim, results)
        else:
            self._set_unregistered_placements(ctx, result_scrim)
        return result_scrim

    def _set_placements_from_results(self, result_scrim: Scrim, results: ScrimResult):
        placement = 1
        for team_tuple in results:
            placement += self._create_placement_teams(placement, result_scrim, team_tuple)

    def _set_unregistered_placements(self, ctx: ScrimContext, result_scrim: Scrim):
        for team in ctx.scrim.teams_manager.get_game_teams():
            result_scrim.teams.append(self._create_placement_team(0, team))

    def _create_placement_teams(self, placement: int, result_scrim: Scrim, team_tuple: tuple[Team]) -> int:
        placement_increment = 0
        for team in team_tuple:
            placement_increment += 1
            result_scrim.teams.append(self._create_placement_team(placement, team))
        return placement_increment

    @staticmethod
    def _create_placement_team(placement: int, team: Team) -> ParticipantTeam:
        participant_team = ParticipantTeam(placement)
        participant_team.team = team
        return participant_team

    def _update_user_ratings(self, ctx: ScrimContext, result: ScrimResult):
        if result is None:
            self._update_unregistered_ratings(ctx)
        else:
            self._update_result_ratings(ctx, result)

    def _update_unregistered_ratings(self, ctx: ScrimContext):
        for player in [player for team in ctx.scrim.teams_manager.get_game_teams() for player in team.members]:
            self._update_user_rating(ctx, player, Result.UNREGISTERED)

    def _update_result_ratings(self, ctx: ScrimContext, result: ScrimResult):
        if len(result[0]) > 1:
            for player in [player for team in result[0] for player in team.members]:
                self._update_user_rating(ctx, player, Result.TIE)
        else:
            for player in result[0][0].members:
                self._update_user_rating(ctx, player, Result.WIN)
        if len(result) > 1:
            losing_teams = [team for group in result[1:] for team in group]
            for player in [player for team in losing_teams for player in team.members]:
                self._update_user_rating(ctx, player, Result.LOSS)

    def _update_user_rating(self, ctx: ScrimContext, user: User, result: Result):
        self._converter.update_user_rating(0, user, ctx.scrim.game, ctx.guild)
