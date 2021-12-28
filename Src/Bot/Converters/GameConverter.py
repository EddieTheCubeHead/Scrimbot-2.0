__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import INFO
from typing import Tuple, List, Dict, Iterator, Set, Any, Union

from discord.ext.commands import Context

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.Game import Game
from Bot.Exceptions.BotLoggedContextException import BotLoggedContextException
from Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Database.DatabaseConnections.GameConnection import GameConnection


@BotDependencyInjector.singleton
class GameConverter(ConverterBase[Game]):

    MISSING_TEXTURE = "https://upload.wikimedia.org/wikipedia/commons/5/59/Minecraft_missing_texture_block.svg"
    connection: GameConnection

    @BotDependencyInjector.inject
    def __init__(self, connection: GameConnection, system_logger: BotSystemLogger):
        super().__init__(connection)
        self.games: Dict[str, Game] = {}
        self._system_logger = system_logger
        self._reserved_alias_names: Set = set()

    def init_games(self, games: dict[str, dict[str, Union[str, int, list[str]]]]):
        for db_game in self.connection.get_all():
            self.games[db_game.name] = db_game
        for game, data in games.items():
            self._init_aliases(game, data)
            try:
                self.add_game(game, data)
            except BotLoggedContextException as exception:
                BotLoggedNoContextException(exception.message, self._system_logger, log=INFO).resolve()

    def add_game(self, game: str, data: dict[str, Union[str, int, list[Alias]]]):
        self._assert_valid_game_name(game)
        if "alias" in data:
            self._assert_valid_aliases(data["alias"])
        self._raw_add_game(game, data)

    async def convert(self, ctx: Context, argument: str) -> Game:
        if argument in self.games:
            return self.games[argument]
        return self._get_game_from_alias(argument)

    def _get_game_from_alias(self, alias: str) -> Game:
        for game in self.games.values():
            if alias in [candidate.name for candidate in game.aliases]:
                return game
        raise BotConversionFailureException("Game", alias)

    @staticmethod
    def _init_aliases(game_name: str, game_data: dict[str, Union[str, int, list[str]]]):
        if "alias" in game_data:
            game_data["alias"] = [Alias(alias, game_name) for alias in game_data["alias"]]

    def _raw_add_game(self, game: str, data: dict[str, Union[str, int, list[Alias]]]):
        min_team_size = data.pop("min_team_size")
        self.games[game] = Game(game, data.pop("colour", "0xffffff"), data.pop("icon", self.MISSING_TEXTURE),
                                min_team_size, data.pop("max_team_size", min_team_size), data.pop("team_count", 2),
                                data.pop("alias", []))
        self.connection.add(self.games[game])

    def _assert_valid_game_name(self, game_name):
        if game_name in self.games:
            raise BotLoggedContextException(f"Cannot initialize two games with the same name ('{game_name}')")

    def _assert_valid_aliases(self, aliases: List[Alias]):
        for alias in aliases:
            if alias.name in self._reserved_alias_names:
                raise BotLoggedContextException(f"Cannot initialize two games with the same alias "
                                                     f"('{alias.name}')")
            self._reserved_alias_names.add(alias.name)
