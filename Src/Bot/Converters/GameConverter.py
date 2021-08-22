__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Tuple, List, Dict, Iterator, Set

from Bot.Converters.ConverterBase import ConverterBase
from Bot.DataClasses.Game import Game
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Bot.Core.ConvertableConstructor import ConvertableConstructor
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@ConvertableConstructor.converter
class GameConverter(ConverterBase[Game]):

    def __init__(self, connection: ConnectionBase):
        super().__init__(connection)
        self.games: Dict[str, Game] = {}
        self._aliases: Set = set()

    def init_games(self, games: Iterator[Tuple[str, str, str, int, int, int, List[str]]]):
        for game in games:
            self.add_game(game)

    def add_game(self, game: Tuple[str, str, str, int, int, int, List[str]]):
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
            if alias in game.aliases:
                return game
        raise BotConversionFailureException("Game", alias)

    def _raw_add_game(self, game: Tuple[str, str, str, int, int, int, List[str]]):
        self.games[game[0]] = Game(*game)

    def _assert_valid_game_name(self, game_name):
        if game_name in self.games:
            raise BotBaseInternalException(f"Cannot initialize two games with the same name ('{game_name}')")

    def _assert_valid_aliases(self, aliases: List[str]):
        for alias in aliases:
            if alias in self._aliases:
                raise BotBaseInternalException(f"Cannot initialize two games with the same alias ('{alias}')")
            self._aliases.add(alias)
