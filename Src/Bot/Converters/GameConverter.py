__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Tuple, List, Dict, Iterator, Set

from Bot.Converters.ConverterBase import ConverterBase
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.Game import Game
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyConstructor.converter
class GameConverter(ConverterBase[Game]):

    def __init__(self, connection: ConnectionBase):
        super().__init__(connection)
        self.games: Dict[str, Game] = {}
        self._reserved_alias_names: Set = set()

    def init_games(self, games: Iterator[Tuple[str, str, str, int, int, int, List[Alias]]]):
        for game in games:
            self.add_game(game)

    def add_game(self, game: Tuple[str, str, str, int, int, int, List[Alias]]):
        self._assert_valid_game_name(game[0])
        if len(game) > 6:
            self._assert_valid_aliases(game[6])
        self._raw_add_game(game)

    def convert(self, argument: str) -> Game:
        if argument in self.games:
            return self.games[argument]
        else:
            return self._get_game_from_alias(argument)

    def _get_game_from_alias(self, alias: str) -> Game:
        for game in self.games.values():
            if alias in [candidate.name for candidate in game.aliases]:
                return game
        raise BotConversionFailureException("Game", alias)

    def _raw_add_game(self, game: Tuple[str, str, str, int, int, int, List[Alias]]):
        self.games[game[0]] = Game(*game)
        self.connection.add(game)

    def _assert_valid_game_name(self, game_name):
        if game_name in self.games:
            raise BotBaseInternalException(f"Cannot initialize two games with the same name ('{game_name}')")

    def _assert_valid_aliases(self, aliases: List[Alias]):
        for alias in aliases:
            if alias.name in self._reserved_alias_names:
                raise BotBaseInternalException(f"Cannot initialize two games with the same alias ('{alias.name}')")
            self._reserved_alias_names.add(alias.name)
