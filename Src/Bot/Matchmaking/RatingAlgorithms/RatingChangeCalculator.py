__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Iterable

from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.Converters.UserRatingConverter import UserRatingConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.DataClasses.UserRating import UserRating
from Bot.DataClasses.UserScrimResult import Result
from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategy import TeamRatingStrategy
from Bot.Matchmaking.RatingAlgorithms.TeamRating.TeamRatingStrategyProvider import TeamRatingStrategyProvider
from Bot.Matchmaking.RatingAlgorithms.UserRatingChange.UserRatingChangeStrategy import UserRatingChangeStrategy
from Bot.Matchmaking.RatingAlgorithms.UserRatingChange.UserRatingChangeStrategyProvider import \
    UserRatingChangeStrategyProvider


def _get_other_team_ratings(team: Team, team_ratings: dict[Team: int]):
    return [team_rating[1] for team_rating in team_ratings.items() if team_rating[0] != team]


@BotDependencyInjector.singleton
class RatingChangeCalculator:

    @BotDependencyInjector.inject
    def __init__(self, user_rating_change_strategy_provider: UserRatingChangeStrategyProvider,
                 team_rating_strategy_provider: TeamRatingStrategyProvider,
                 rating_converter: UserRatingConverter):
        self._user_rating_change_strategy_provider = user_rating_change_strategy_provider
        self._team_rating_strategy_provider = team_rating_strategy_provider
        self._rating_converter = rating_converter

    def calculate_changes(self, game: Game, guild: Guild, results: ScrimResult) -> dict[User: int]:
        team_strategy = self._team_rating_strategy_provider.get_strategy(game.name)
        user_strategy = self._user_rating_change_strategy_provider.get_strategy(game.name)
        flattened_teams = [team for team_group in results for team in team_group]
        flattened_players = [player for team in flattened_teams for player in team.members]
        player_ratings = {
            player: self._rating_converter.get_user_rating(player, game, guild) for player in flattened_players
        }
        team_ratings = {team: self._get_team_rating(team, team_strategy, player_ratings) for team in flattened_teams}
        player_rating_changes = {}
        if len(results[0]) > 1:
            self._get_tying_rating_changes(results[0], team_ratings, player_rating_changes, user_strategy,
                                           player_ratings)
        else:
            self._update_team_ratings(results[0][0], user_strategy, player_ratings, team_ratings, player_rating_changes,
                                      Result.WIN)
        if len(results) > 1:
            losing_teams = [team for group in results[1:] for team in group]
            self._get_losing_rating_changes(losing_teams, team_ratings, player_rating_changes, user_strategy,
                                            player_ratings)
        return player_rating_changes

    @staticmethod
    def _get_team_rating(team: Team, strategy: TeamRatingStrategy, player_ratings: dict[User: int]):
        member_ratings = [player_ratings[player] for player in team.members]
        return strategy.get_rating(*member_ratings)

    def _get_tying_rating_changes(self, teams: Iterable[Team], team_ratings: dict[Team: int],
                                  player_rating_changes: dict[User, int], user_strategy: UserRatingChangeStrategy,
                                  player_ratings: dict[User: UserRating]):
        for team in teams:
            self._update_team_ratings(team, user_strategy, player_ratings, team_ratings, player_rating_changes,
                                      Result.TIE)

    def _get_losing_rating_changes(self, teams: Iterable[Team], team_ratings: dict[Team: int],
                                   player_rating_changes: dict[User, int], user_strategy: UserRatingChangeStrategy,
                                   player_ratings: dict[User: UserRating]):
        for team in teams:
            self._update_team_ratings(team, user_strategy, player_ratings, team_ratings, player_rating_changes,
                                      Result.LOSS)

    @staticmethod
    def _update_team_ratings(team: Team, user_strategy: UserRatingChangeStrategy,
                             player_ratings: dict[User: UserRating], team_ratings: dict[Team, int],
                             player_rating_changes: dict[User: UserRating], result: Result):
        other_team_ratings = _get_other_team_ratings(team, team_ratings)
        for player in team.members:
            player_rating_changes[player] = user_strategy.get_rating_change(player_ratings[player], result,
                                                                            team_ratings[team], *other_team_ratings)
