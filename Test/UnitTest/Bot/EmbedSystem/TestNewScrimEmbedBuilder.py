__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from discord import Embed, Color

from Bot.DataClasses.Game import Game
from Bot.DataClasses.User import User
from Bot.EmbedSystem.NewScrimEmbedBuilder import NewScrimEmbedBuilder
from Test.Utils.TestBases.EmbedUnittest import EmbedUnittest
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_mock_player(user_id):
    return User(user_id=user_id)


class TestNewScrimEmbedBuilder(EmbedUnittest):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_builder = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_state_provider = MagicMock()
        self.builder = NewScrimEmbedBuilder(self.mock_state_provider)
        self.scrim_state = MagicMock()
        self.mock_game = self._create_mock_game("Test", 2, 5)
        self.scrim = MagicMock()
        self.scrim.game = self.mock_game
        self.mock_state_provider.resolve_from_key.return_value = self.scrim_state
        self.context = MagicMock()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(NewScrimEmbedBuilder)

    def test_build_given_scrim_manager_then_manager_state_build_methods_called_and_embed_constructed_from_output(self):
        self.scrim_state.build_description.return_value = "Correct description"
        self.scrim_state.build_fields.return_value = ([("Correct", "fields", True)])
        self.scrim_state.build_footer.return_value = "Correct footer"
        actual = self.builder.build(self.context, self.scrim)
        self.assertEqual("Status", actual.title)
        self.assertEqual(f"Correct description", actual.description)
        self._assert_correct_fields(actual, ("Correct", "fields", True))
        self.assertEqual("Correct footer", actual.footer.text)
        self._assert_game_fields(actual)
        self.mock_state_provider.resolve_from_key.assert_called_with(self.scrim.state)
        self.scrim_state.build_description.assert_called_with(self.scrim)
        self.scrim_state.build_fields.assert_called_with(self.scrim)
        self.scrim_state.build_footer.assert_called_with(self.scrim)

    def _create_mock_game(self, name, team_count, min_team_size, max_team_size=None) -> Game:
        mock_game = MagicMock()
        mock_game.name = name
        mock_game.team_count = team_count
        mock_game.min_team_size = min_team_size
        mock_game.max_team_size = max_team_size if max_team_size is not None else min_team_size
        mock_game.icon = str(self.id_builder.generate_viable_id())
        mock_game.colour = self.id_builder.generate_viable_id()
        return mock_game

    def _assert_game_fields(self, embed: Embed):
        self.assertEqual(f"{self.mock_game.name} scrim", embed.author.name)
        self.assertEqual(self.mock_game.icon, embed.author.icon_url)
        self.assertEqual(Color(self.mock_game.colour), embed.colour)
