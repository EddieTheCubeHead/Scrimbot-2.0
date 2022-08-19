__version__ = "0.1"
__author__ = "Eetu Asikainen"

import random
from collections.abc import Iterator

from Bot.Converters.TeamCreationStrategyConverter import TeamCreationStrategyConverter
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Matchmaking.TeamCreation.TeamCreationStrategy import TeamCreationStrategy


def _next_team_iterator(team_count: int) -> Iterator[int]:
    next_team = 0
    while True:
        yield next_team
        next_team += 1
        next_team %= team_count


@TeamCreationStrategyConverter.register("random")
class RandomTeamsStrategy(TeamCreationStrategy):

    def _create_teams_hook(self, teams_manager: ScrimTeamsManager):
        players = teams_manager.get_standard_teams()[0].members.copy()
        teams = [[] for _ in range(teams_manager.game.team_count)]
        team_iterator = _next_team_iterator(teams_manager.game.team_count)
        while players:
            team_index = next(team_iterator)
            teams[team_index].append(players.pop(random.randint(0, len(players) - 1)))

        for team_index, team in enumerate(teams):
            for player in team:
                teams_manager.set_team(team_index, player)
