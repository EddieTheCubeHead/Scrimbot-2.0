__version__ = "0.1"
__author__ = "Eetu Asikainen"

import random
from collections.abc import Iterator

from Src.Bot.Converters.TeamCreationStrategyConverter import TeamCreationStrategyConverter
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.Team import PARTICIPANTS
from Src.Bot.Matchmaking.TeamCreation.TeamCreationStrategy import TeamCreationStrategy


def _next_team_iterator(team_count: int) -> Iterator[int]:
    next_team = 0
    while True:
        yield next_team
        next_team += 1
        next_team %= team_count


@TeamCreationStrategyConverter.register("random")
class RandomTeamsStrategy(TeamCreationStrategy):

    def _create_teams_hook(self, scrim: Scrim):
        players = next(team.team for team in scrim.teams if team.team.name == PARTICIPANTS).members.copy()
        teams = [[] for _ in range(scrim.game.team_count)]
        team_iterator = _next_team_iterator(scrim.game.team_count)
        while players:
            team_index = next(team_iterator)
            teams[team_index].append(players.pop(random.randint(0, len(players) - 1)))

        for team_index, team in enumerate(teams):
            for player in team:
                self._team_service.remove_from_team(scrim, player)
                self._team_service.add_to_team(scrim, player, f"Team {team_index + 1}")
