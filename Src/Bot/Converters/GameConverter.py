__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import INFO
from typing import Tuple, List, Dict, Iterator, Set, Any, Union

from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.Converters.ConverterBase import ConverterBase
from Src.Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Src.Bot.DataClasses.Alias import Alias
from Src.Bot.DataClasses.Game import Game
from Src.Bot.Exceptions.BotLoggedContextException import BotLoggedContextException
from Src.Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException
from Src.Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Src.Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Src.Database.DatabaseConnections.GameConnection import GameConnection


@HinteDI.singleton
class GameConverter(ConverterBase[Game]):

    MISSING_TEXTURE = "https://upload.wikimedia.org/wikipedia/commons/5/59/Minecraft_missing_texture_block.svg"
    connection: GameConnection

    @HinteDI.inject
    def __init__(self, connection: GameConnection, system_logger: BotSystemLogger):
        super().__init__(connection)
        self.games: Dict[str, Game] = {}
        self._system_logger = system_logger
        self._reserved_alias_names: Set = set()

    def init_games(self, games: dict[str, dict[str, Union[str, int, list[str]]]]):
        if self.games:
            return
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
        reason = "argument did not correspond to any name or alias for a registered game"
        raise BotConversionFailureException("Game", alias, reason=reason)

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
