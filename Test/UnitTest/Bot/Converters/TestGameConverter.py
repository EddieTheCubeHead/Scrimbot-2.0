__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.Game import Game
from Bot.Converters.GameConverter import GameConverter
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Bot.Core.ConvertableConstructor import ConvertableConstructor


class TestGameConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.provider = GameConverter(self.connection)

    def test_init_given_normal_init_then_converter_for_game_dataclass_set(self):
        self.assertIn(GameConverter, ConvertableConstructor.converters.values())

    def test_init_games_given_valid_game_data_list_then_all_games_build(self):
        game_names = ["Dota 2", "CS:GO", "Valorant", "Test"]
        fake_games_generator = (game for game in self._build_fake_games_tuples(*game_names))
        self.provider.init_games(fake_games_generator)
        for name in game_names:
            self.assertIn(name, self.provider.games)

    def test_init_games_given_duplicate_names_then_error_raised(self):
        shared_name = "Test"
        game_1 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        game_2 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same name ('{shared_name}')")
        self._assert_raises_correct_exception(expected_exception, self.provider.init_games,
                                              (game for game in [game_1, game_2]))

    def test_init_games_given_duplicate_aliases_then_error_raised(self):
        shared_alias = "Test"
        game_1 = ("CS:GO", "0xffffff", "icon_url", 5, 5, 2, [shared_alias])
        game_2 = ("Dota 2", "0xffffff", "icon_url", 5, 5, 2, [shared_alias])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same alias ('{shared_alias}')")
        self._assert_raises_correct_exception(expected_exception, self.provider.init_games,
                                              (game for game in [game_1, game_2]))

    def test_add_game_given_valid_game_then_successful(self):
        new_game_name = "New game"
        existing_game = (new_game_name, "0xffffff", "icon_url", 5, 5, 2, ["alias"])
        self.provider.add_game(existing_game)
        self.assertIn(new_game_name, self.provider.games)

    def test_add_game_given_duplicate_names_then_error_raised(self):
        shared_name = "Test"
        game_1 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        game_2 = (shared_name, "0xffffff", "icon_url", 5, 5, 2, [])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same name ('{shared_name}')")
        self.provider.add_game(game_1)
        self._assert_raises_correct_exception(expected_exception, self.provider.add_game, game_2)

    def test_add_game_given_duplicate_aliases_then_error_raised(self):
        shared_alias = "Test"
        game_1 = ("CS:GO", "0xffffff", "icon_url", 5, 5, 2, [shared_alias])
        game_2 = ("Dota 2", "0xffffff", "icon_url", 5, 5, 2, [shared_alias])
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same alias ('{shared_alias}')")
        self.provider.add_game(game_1)
        self._assert_raises_correct_exception(expected_exception, self.provider.add_game, game_2)

    def test_convert_given_existing_game_name_then_correct_game_returned(self):
        game_name = "Dota 2"
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 5, 2, ["dota"])
        self.provider.games[game_name] = new_game
        self.assertEqual(new_game, self.provider.convert(game_name))

    def test_convert_given_existing_alias_then_correct_game_returned(self):
        game_name = "Dota 2"
        game_alias = "dota"
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 5, 2, [game_alias])
        self.provider.games[game_name] = new_game
        self.assertEqual(new_game, self.provider.convert(game_alias))

    def test_convert_given_argument_with_no_hits_then_error_raised(self):
        invalid_argument = "Nonexistent"
        expected_exception = BotConversionFailureException("Game", invalid_argument)
        self._assert_raises_correct_exception(expected_exception, self.provider.convert, invalid_argument)

    def _build_fake_games_tuples(self, *names: str):
        games_tuples = []
        for name in names:
            games_tuples.append(self._build_fake_game_tuple(name))
        return games_tuples

    def _build_fake_game_tuple(self, name: str):
        return name, "0xffffff", "icon_url", 5, 5, 2, [str(self.id_mocker.generate_viable_id()) for _ in range(3)]
