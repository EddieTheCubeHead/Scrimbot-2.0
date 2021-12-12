__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Any
from unittest.mock import MagicMock

from Bot.DataClasses.Alias import Alias
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.Game import Game
from Bot.Converters.GameConverter import GameConverter
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException


class TestGameConverter(AsyncUnittestBase):

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
        fake_games = self._build_fake_games_dict(*game_names)
        self.converter.init_games(fake_games)
        for name in game_names:
            self.assertIn(name, self.converter.games)

    def test_init_games_given_duplicate_aliases_then_error_raised(self):
        shared_alias = "Test"
        games = {"CS:GO": {"colour": "0xffffff",
                           "icon": "icon_url",
                           "min_team_size": 5,
                           "alias": [shared_alias]},
                 "Dota 2": {"colour": "0xffffff",
                            "icon": "icon_url",
                            "min_team_size": 5,
                            "alias": [shared_alias]}}
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same alias ('{shared_alias}')")
        self._assert_raises_correct_exception(expected_exception, self.converter.init_games,
                                              games)

    def test_add_game_given_valid_game_then_successful(self):
        new_game_name = "New game"
        new_game = {"colour": "0xffffff", "icon": "icon_url", "min_team_size": 5, "max_team_size": 7,
                    "team_count": 3, "alias": [Alias("alias", new_game_name)]}
        self.converter.add_game(new_game_name, new_game)
        self.assertIn(new_game_name, self.converter.games)
        self.connection.add.assert_called()

    def test_add_game_given_duplicate_names_then_error_raised(self):
        shared_name = "Test"
        game_1 = {"colour": "0xffffff", "icon": "icon_url", "min_team_size": 5}
        game_2 = {"colour": "0xffffff", "icon": "icon_url", "min_team_size": 5}
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same name ('{shared_name}')")
        self.converter.add_game(shared_name, game_1)
        self._assert_raises_correct_exception(expected_exception, self.converter.add_game, shared_name, game_2)

    def test_add_game_given_duplicate_aliases_then_error_raised(self):
        shared_alias = "Test"
        games = {"CS:GO": {"colour": "0xffffff",
                           "icon": "icon_url",
                           "min_team_size": 5,
                           "alias": [Alias(shared_alias, "CS:GO")]},
                 "Dota 2": {"colour": "0xffffff",
                            "icon": "icon_url",
                            "min_team_size": 5,
                            "alias": [Alias(shared_alias, "Dota 2")]}}
        expected_exception = \
            BotBaseInternalException(f"Cannot initialize two games with the same alias ('{shared_alias}')")
        self.converter.add_game("CS:GO", games.pop("CS:GO"))
        self._assert_raises_correct_exception(expected_exception, self.converter.add_game, "Dota 2",
                                              games.pop("Dota 2"))

    async def test_convert_given_existing_game_name_then_correct_game_returned(self):
        game_name = "Dota 2"
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 5, 2, [Alias("dota", game_name)])
        self.converter.games[game_name] = new_game
        self.assertEqual(new_game, await self.converter.convert(MagicMock(), game_name))

    async def test_convert_given_existing_alias_then_correct_game_returned(self):
        game_name = "Dota 2"
        game_alias = Alias("dota", game_name)
        new_game = Game(game_name, "0xffffff", "icon_url", 5, 5, 2, [game_alias])
        self.converter.games[game_name] = new_game
        self.assertEqual(new_game, await self.converter.convert(MagicMock(), game_alias.name))

    async def test_convert_given_argument_with_no_hits_then_error_raised(self):
        invalid_argument = "Nonexistent"
        expected_exception = BotConversionFailureException("Game", invalid_argument)
        await self._async_assert_raises_correct_exception(expected_exception, self.converter.convert, MagicMock(),
                                                          invalid_argument)

    def _build_fake_games_dict(self, *names: str) -> dict[str, Any]:
        return {name: {"colour": "0xffffff",
                       "icon": "icon_url",
                       "min_team_size": 5,
                       "alias": [str(self.id_mocker.generate_viable_id()) for _ in range(3)]}
                for name in names}
