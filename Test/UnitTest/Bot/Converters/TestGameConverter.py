__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.Alias import Alias
from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.Game import Game
from Bot.Converters.GameConverter import GameConverter
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Bot.Core.BotDependencyInjector import BotDependencyInjector


class TestGameConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.converter = GameConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(GameConverter)

    def test_init_games_given_valid_game_data_list_then_all_games_build(self):
        game_names = ["Dota 2", "CS:GO", "Valorant", "Test"]
        fake_games_generator = (game for game in self._build_fake_games_tuples(*game_names))
        self.converter.init_games(fake_games_generator)
        for name in game_names:
            self.assertIn(name, self.converter.games)

    def test_init_games_given_duplicate_names_then_error_raised(self):
        shared_name = "Test"
        game_1 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        game_2 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same name ('{shared_name}')")
        self._assert_raises_correct_exception(expected_exception, self.converter.init_games,
                                              (game for game in [game_1, game_2]))

    def test_init_games_given_duplicate_aliases_then_error_raised(self):
        shared_alias = "Test"
        game_1 = ("CS:GO", "0xffffff", "icon_url", 5, 5, 2, [Alias(shared_alias, "CS:GO")])
        game_2 = ("Dota 2", "0xffffff", "icon_url", 5, 5, 2, [Alias(shared_alias, "Dota 2")])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same alias ('{shared_alias}')")
        self._assert_raises_correct_exception(expected_exception, self.converter.init_games,
                                              (game for game in [game_1, game_2]))

    def test_add_game_given_valid_game_then_successful(self):
        new_game_name = "New game"
        new_game = (new_game_name, "0xffffff", "icon_url", 5, 5, 2, [Alias("alias", new_game_name)])
        self.converter.add_game(new_game)
        self.assertIn(new_game_name, self.converter.games)
        self.connection.add.assert_called_with(new_game)

    def test_add_game_given_duplicate_names_then_error_raised(self):
        shared_name = "Test"
        game_1 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        game_2 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same name ('{shared_name}')")
        self.converter.add_game(game_1)
        self._assert_raises_correct_exception(expected_exception, self.converter.add_game, game_2)

    def test_add_game_given_duplicate_aliases_then_error_raised(self):
        shared_alias = "Test"
        game_1 = ("CS:GO", "0xffffff", "icon_url", 5, 5, 2, [Alias(shared_alias, "CS:GO")])
        game_2 = ("Dota 2", "0xffffff", "icon_url", 5, 5, 2, [Alias(shared_alias, "Dota 2")])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same alias ('{shared_alias}')")
        self.converter.add_game(game_1)
        self._assert_raises_correct_exception(expected_exception, self.converter.add_game, game_2)

    def test_convert_given_existing_game_name_then_correct_game_returned(self):
        game_name = "Dota 2"
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 5, 2, [Alias("dota", game_name)])
        self.converter.games[game_name] = new_game
        self.assertEqual(new_game, self.converter.convert(game_name))

    def test_convert_given_existing_alias_then_correct_game_returned(self):
        game_name = "Dota 2"
        game_alias = Alias("dota", game_name)
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 5, 2, [game_alias])
        self.converter.games[game_name] = new_game
        self.assertEqual(new_game, self.converter.convert(game_alias.name))

    def test_convert_given_argument_with_no_hits_then_error_raised(self):
        invalid_argument = "Nonexistent"
        expected_exception = BotConversionFailureException("Game", invalid_argument)
        self._assert_raises_correct_exception(expected_exception, self.converter.convert, invalid_argument)

    def _build_fake_games_tuples(self, *names: str):
        games_tuples = []
        for name in names:
            games_tuples.append(self._build_fake_game_tuple(name))
        return games_tuples

    def _build_fake_game_tuple(self, name: str):
        return name, "0xffffff", "icon_url", 5, 5, 2,\
               [Alias(str(self.id_mocker.generate_viable_id()), name) for _ in range(3)]
