__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.Matchmaking.RatingAlgorithms.UserRatingChange.FlatChangeStrategy import FlatChangeStrategy
from Bot.Matchmaking.RatingAlgorithms.UserRatingChange.UserRatingChangeStrategy import UserRatingChangeStrategy


@HinteDI.singleton
class UserRatingChangeStrategyProvider:

    @HinteDI.inject
    def __init__(self, flat_change_strategy: FlatChangeStrategy):
        self._default_strategy = flat_change_strategy
        self._strategies: dict[str, UserRatingChangeStrategy] = {flat_change_strategy.name: flat_change_strategy}

    def get_strategy(self, strategy_name: str) -> UserRatingChangeStrategy:
        if strategy_name in self._strategies:
            return self._strategies[strategy_name]
        return self._default_strategy
