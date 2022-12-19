__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from sqlalchemy.exc import NoResultFound

from Src.Bot.DataClasses.Alias import Alias
from Src.Bot.DataClasses.Game import Game
from Src.Configs.Config import Config
from Src.Database.Core.MasterConnection import MasterConnection
from Test.Utils.TestBases.ConnectionUnittest import ConnectionUnittest
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Src.Database.DatabaseConnections.GameConnection import GameConnection


_test_games = {
  "Dota 2": {
    "min_team_size": 5,
    "icon": "https://i.imgur.com/OlWIlyY.jpg?1",
    "colour": "0xce0000",
    "alias": [ "dota2", "dota" ]
  },
  "CS:GO": {
    "min_team_size": 5,
    "icon": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/6d/6d448876809d7b79aa8f070271c07b1296459400_full.jpg",
    "colour": "0xff8c1a",
    "alias": [ "cs", "counterstrike", "csgo" ]
  },
  "Overwatch": {
    "min_team_size": 6,
    "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1200px-Overwatch_circle_logo.svg.png",
    "colour": "0xffa31a",
    "alias": [ "ow", "overwatch" ]
  }
}


def _construct_game(name, data) -> Game:
    return Game(name, data["colour"], data["icon"], data["min_team_size"],
                data.pop("max_team_size", data["min_team_size"]), data.pop("team_count", 2),
                [Alias(alias, name) for alias in data.pop("alias", [])])


def _construct_games(games_dict) -> list[Game]:
    games: list[Game] = []
    for name, data in games_dict.items():
        games.append(_construct_game(name, data))

    return games


class TestGameConnection(ConnectionUnittest[Game]):

    master: MasterConnection = None
    config: Config = None

    # noinspection PyPropertyAccess
    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = MagicMock()
        cls.config.games_dict = _test_games
        cls.master = MasterConnection(cls.config, ":memory:")
        with cls.master.get_session() as session:
            games = _construct_games(cls.config.games_dict)
            session.add_all(games)

    def setUp(self) -> None:
        self.connection: GameConnection = GameConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(GameConnection)

    def test_init_given_no_games_in_db_then_loads_config(self):
        games_config = self.config.games_dict
        for game in games_config:
            with self.subTest(f"Initializing games from config ({game})"):
                actual = self.connection.get_game(game)
                self._assert_successful_fetch(actual)

    def test_get_game_when_querying_with_an_alias_then_corresponding_game_found(self):
        aliases = ["dota", "cs", "ow"]
        for alias in aliases:
            with self.subTest(f"Querying games with an alias ({alias})"):
                actual = self.connection.get_game(alias)
                self._assert_successful_fetch(actual)

    def test_get_game_when_no_game_found_then_exception_raised(self):
        invalid_game_name = f"Game{self.id_generator.generate_nonviable_id()}"
        expected_exception = NoResultFound("No row was found when one was required")
        self._assert_raises_correct_exception(expected_exception, self.connection.get_game, invalid_game_name)

    def test_add_given_valid_game_then_game_and_aliases_added(self):
        game_name = f"Game{self.id_generator.generate_viable_id()}"
        alias = "New alias"
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 8, 3, [Alias(alias, game_name)])
        self.connection.add(new_game)
        with self.master.get_session() as session:
            session.query(Game).filter(Game.name == game_name).one()
            session.query(Alias).filter(Alias.name == alias).one()

    def test_get_all_given_called_then_all_games_from_database_returned(self):
        games = self.connection.get_all()
        for game_name in self.config.games_dict:
            self.assertIn(game_name, [game.name for game in games])
