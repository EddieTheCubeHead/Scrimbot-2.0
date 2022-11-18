__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.Matchmaking.RatingAlgorithms.TeamRating.MeanRatingStrategy import MeanRatingStrategy
from Bot.Matchmaking.RatingAlgorithms.TeamRating.WeightBestPlayerRatingStrategy import WeightBestPlayerRatingStrategy


@HinteDI.singleton
class TeamRatingStrategyProvider:

    @HinteDI.inject
    def __init__(self, mean_strategy: MeanRatingStrategy, weight_best_player_strategy: WeightBestPlayerRatingStrategy):
        self._default_strategy = mean_strategy
        self._strategies = {strategy.name: strategy for strategy in (mean_strategy, weight_best_player_strategy)}

    def get_strategy(self, name: str):
        if name in self._strategies:
            return self._strategies[name]
        return self._default_strategy
