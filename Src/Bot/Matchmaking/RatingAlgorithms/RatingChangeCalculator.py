__version__ = "0.1"
__author__ = "Eetu Asikainen"

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
            for team in results[0]:
                other_team_ratings = _get_other_team_ratings(team, team_ratings)
                for player in team.members:
                    player_rating_changes[player] = user_strategy.get_rating_change(player_ratings[player], Result.TIE,
                                                                                    team_ratings[team],
                                                                                    *other_team_ratings)
        else:
            for player in results[0][0].members:
                team = results[0][0]
                other_team_ratings = _get_other_team_ratings(team, team_ratings)
                player_rating_changes[player] = user_strategy.get_rating_change(player_ratings[player], Result.WIN,
                                                                                team_ratings[team],
                                                                                *other_team_ratings)
        if len(results) > 1:
            losing_teams = [team for group in results[1:] for team in group]
            for team in losing_teams:
                other_team_ratings = _get_other_team_ratings(team, team_ratings)
                for player in team.members:
                    player_rating_changes[player] = user_strategy.get_rating_change(player_ratings[player], Result.LOSS,
                                                                                    team_ratings[team],
                                                                                    *other_team_ratings)
        return player_rating_changes

    @staticmethod
    def _get_team_rating(team: Team, strategy: TeamRatingStrategy, player_ratings: dict[User: int]):
        member_ratings = [player_ratings[player] for player in team.members]
        return strategy.get_rating(*member_ratings)
