__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.exc import NoResultFound

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.Game import Game
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Utils.ConnectionUnittest import ConnectionUnittest
from Utils.TestIdGenerator import TestIdGenerator
from Database.DatabaseConnections.GameConnection import GameConnection


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

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.master = MasterConnection(":memory:")
        with cls.master.get_session() as session:
            games = _construct_games(Config.games_dict)
            session.add_all(games)

    def setUp(self) -> None:
        self.connection: GameConnection = GameConnection(self.master)

    def test_init_given_normal_init_then_connection_for_game_dataclass_set(self):
        self.assertIn(GameConnection, BotDependencyInjector.dependencies)

    def test_init_given_no_games_in_db_then_loads_config(self):
        games_config = Config.games_dict
        for game in games_config:
            with self.subTest(f"Initializing games from config ({game})"):
                actual = self.connection.get_game(game)
                self._assert_successful_fetch(actual)

    def test_get_game_when_querying_with_an_alias_then_corresponding_game_found(self):
        aliases = ["dota", "cs", "t"]
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
