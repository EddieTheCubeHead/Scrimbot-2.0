__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Utils.UnittestBase import UnittestBase
from Configs.Config import Config


class TestConfig(UnittestBase):

    def setUp(self) -> None:
        self.config: Config = Config()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(Config)

    def test_games_dict_given_json_file_then_file_read_and_set_as_property(self):
        for name, game in self.config.games_dict.items():
            self._assert_correct_game_data(name, game)

    def _assert_correct_game_data(self, name, game):
        self.assertIsInstance(name, str)
        self.assertIsInstance(game["min_team_size"], int)
        self.assertIsInstance(game["colour"], str)
        self.assertIsInstance(game["icon"], str)
        self.assertIsInstance(game["alias"], list)

    def test_token_given_secrets_file_exists_then_file_read_and_token_set(self):
        self.assertIsInstance(self.config.token, str)

    def test_database_name_given_configs_file_exists_then_file_read_and_token_set(self):
        self.assertIsInstance(self.config.database_name, str)
