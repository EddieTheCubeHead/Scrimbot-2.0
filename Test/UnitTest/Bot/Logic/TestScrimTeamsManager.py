__version__ = "0.1"
__author__ = "Eetu Asikainen"

import random
import unittest
from unittest.mock import MagicMock, AsyncMock

from discord import Guild, Member

from Bot.DataClasses.User import User
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Bot.DataClasses.Game import Game
from Bot.DataClasses.Team import Team
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Bot.Exceptions.BotLoggedContextException import BotLoggedContextException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


def _create_mock_game(min_size, max_size, team_count):
    mock_game = Game("Test", "0xffffff", "icon", min_size, max_size, team_count)
    return mock_game


def generate_mock_voice_state(guild_id: int):
    mock_guild = MagicMock()
    mock_channel = MagicMock()
    mock_voice_state = MagicMock()
    mock_guild.id = guild_id
    mock_channel.guild = mock_guild
    mock_voice_state.channel = mock_channel
    return mock_voice_state


def generate_mock_voice_channel(channel_id: int, team: Team = None, guild: Guild = None) -> VoiceChannel:
    mock_channel: VoiceChannel = MagicMock()
    mock_channel.channel_id = channel_id
    mock_channel.teams = [team]
    if guild is not None:
        mock_channel.parent_channel.guild_id = guild.id
    return mock_channel


class TestScrimTeamsManager(AsyncUnittestBase):

    mocked_voice_states: dict[int, MagicMock] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.participant_manager = MagicMock()
        self.participant_manager.try_get_participant.side_effect = self._get_mocked_voice_state
        self.channel_provider = MagicMock()

    def _get_mocked_voice_state(self, player_id: int):
        if player_id in self.mocked_voice_states:
            return self.mocked_voice_states[player_id]

    def test_init_given_team_count_zero_then_internal_error_raised(self):
        mock_game = _create_mock_game(5, 5, 0)
        expected_exception = BotLoggedContextException("Tried to initialize a teams manager for a game with less"
                                                       " than 1 teams.")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager)

    def test_init_given_team_min_size_larger_than_max_size_when_max_size_not_zero_then_internal_error_raised(self):
        mock_game = _create_mock_game(5, 3, 1)
        expected_exception = BotLoggedContextException("Tried to initialize a teams manager for a game with "
                                                       "smaller team max size than team min size.")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager)

    def test_init_given_team_min_size_larger_than_max_size_when_unlimited_max_size_then_init_successful(self):
        self._setup_manager(5, 0, 1)

    def test_init_given_premade_team_with_identical_sizes_as_game_then_init_successful(self):
        team_name = "Valid team"
        mock_game = _create_mock_game(5, 6, 2)
        valid_team = Team(team_name, [], 5, 6)
        manager = ScrimTeamsManager(mock_game, self.participant_manager, teams=[valid_team])
        self.assertEqual(team_name, manager.get_game_teams()[0].name)

    def test_init_given_premade_team_with_stricter_but_valid_sizes_as_game_then_init_successful(self):
        team_name = "Valid team"
        mock_game = _create_mock_game(4, 7, 2)
        valid_team = Team(team_name, [], 5, 6)
        manager = ScrimTeamsManager(mock_game, self.participant_manager, teams=[valid_team])
        self.assertEqual(team_name, manager.get_game_teams()[0].name)

    def test_init_given_premade_team_when_team_name_conflicts_with_standard_teams_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        invalid_team = Team(ScrimTeamsManager.PARTICIPANTS)
        expected_exception = \
            BotBaseRespondToContextException(f"Cannot create a scrim with a premade team name conflicting with a "
                                             f"name reserved for standard teams ({ScrimTeamsManager.PARTICIPANTS})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager, teams=[invalid_team])

    def test_init_given_duplicate_premade_team_names_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        duplicate_name = "Duplicate team"
        team_1 = Team(duplicate_name, [], 5, 5)
        team_2 = Team(duplicate_name, [], 5, 5)
        expected_exception = \
            BotBaseRespondToContextException(f"Cannot create a scrim with premade teams having identical names "
                                             f"({duplicate_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager, teams=[team_1, team_2])

    def test_init_given_duplicate_premade_team_names_when_name_conflicts_with_standard_teams_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        duplicate_name = ScrimTeamsManager.SPECTATORS
        team_1 = Team(duplicate_name)
        team_2 = Team(duplicate_name)
        expected_exception = \
            BotBaseRespondToContextException(f"Cannot create a scrim with a premade team name conflicting with a name "
                                             f"reserved for standard teams ({duplicate_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager, teams=[team_1, team_2])

    def test_init_given_invalid_sized_premade_team_min_players_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        team_name = "Invalid team"
        invalid_team = Team(team_name, [], 3, 5)
        expected_exception = \
            BotBaseRespondToContextException(f"Cannot create a scrim with a premade team with a size incompatible with "
                                             f"the chosen game ({team_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager, teams=[invalid_team])

    def test_init_given_invalid_sized_premade_team_max_players_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        team_name = "Invalid team"
        invalid_team = Team(team_name, [], 5, 7)
        expected_exception = \
            BotBaseRespondToContextException(f"Cannot create a scrim with a premade team with a size incompatible with "
                                             f"the chosen game ({team_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager, teams=[invalid_team])

    def test_init_given_premade_team_with_too_many_players_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        team_name = "Invalid team"
        mock_players = [self._create_mock_user() for _ in range(6)]
        invalid_team = Team(team_name, mock_players, 5, 5)
        expected_exception = \
            BotBaseRespondToContextException(f"Cannot create a scrim with a premade team with a size incompatible with "
                                             f"the chosen game ({team_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game,
                                              self.participant_manager, teams=[invalid_team])

    def test_init_given_valid_team_voice_channels_then_corresponding_game_team_channels_set(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_game = _create_mock_game(min_size, max_size, team_count)
        channel_ids = self.id_generator.generate_viable_id_group(team_count)
        mock_team = MagicMock()
        teams_channels = [generate_mock_voice_channel(channel_id, mock_team) for channel_id in channel_ids]
        manager = ScrimTeamsManager(mock_game, self.participant_manager, team_channels=teams_channels)
        for team, channel in zip(manager.get_game_teams(), teams_channels):
            self.assertEqual(team.voice_channel, channel)

    def test_init_given_valid_lobby_channel_then_standard_team_channels_set(self):
        min_size, max_size, team_count = 3, 4, 5
        mock_game = _create_mock_game(min_size, max_size, team_count)
        lobby_channel = generate_mock_voice_channel(self.id_generator.generate_viable_id())
        manager = ScrimTeamsManager(mock_game, self.participant_manager, team_channels=[], lobby=lobby_channel)
        for team in manager.get_standard_teams():
            self.assertEqual(team.voice_channel, lobby_channel)

    def test_init_given_too_many_voice_channels_then_only_needed_channels_assigned(self):
        min_size, max_size, team_count = 2, 7, 4
        mock_game = _create_mock_game(min_size, max_size, team_count)
        channel_ids = self.id_generator.generate_viable_id_group(team_count + 1)
        teams_channels = [generate_mock_voice_channel(channel_id) for channel_id in channel_ids]
        manager = ScrimTeamsManager(mock_game, self.participant_manager, team_channels=teams_channels)
        for team in manager.get_game_teams():
            self.assertIn(team.voice_channel, teams_channels)
        for team in manager.get_standard_teams():
            self.assertIsNone(team.voice_channel)

    def test_get_standard_teams_given_valid_setup_then_all_standard_teams_returned(self):
        min_size, max_size, team_count = 5, 5, 2
        manager = self._setup_manager(min_size, max_size, team_count)
        standard_teams = manager.get_standard_teams()
        self._assert_valid_standard_teams(standard_teams, max_size, min_size, team_count)

    def test_get_game_teams_given_valid_setup_when_no_premade_teams_then_correct_teams_returned(self):
        min_size, max_size, team_count = 5, 6, 4
        manager = self._setup_manager(min_size, max_size, team_count)
        game_teams = manager.get_game_teams()
        self._assert_valid_game_teams(game_teams, max_size, min_size, team_count)

    def test_get_game_teams_given_valid_setup_with_partly_premade_teams_then_correct_teams_returned(self):
        min_size, max_size, team_count = 5, 6, 4
        mock_game = _create_mock_game(min_size, max_size, team_count)
        mock_team = Team("Premade team", [], min_size, max_size)
        manager = ScrimTeamsManager(mock_game, self.participant_manager, teams=[mock_team])
        game_teams = manager.get_game_teams()
        self.assertEqual(mock_team, game_teams[0])
        self._assert_valid_game_teams(game_teams, max_size, min_size, team_count)

    def test_get_game_teams_given_valid_setup_with_only_premade_teams_then_correct_teams_returned(self):
        min_size, max_size, team_count = 5, 6, 4
        mock_game = _create_mock_game(min_size, max_size, team_count)
        mock_teams = [Team(f"Premade {i + 1}", [], min_size, max_size) for i in range(team_count)]
        manager = ScrimTeamsManager(mock_game, self.participant_manager, teams=mock_teams)
        game_teams = manager.get_game_teams()
        self.assertEqual(mock_teams, game_teams)
        self._assert_valid_game_teams(game_teams, max_size, min_size, team_count)

    def test_add_player_given_participants_not_full_when_player_added_to_participants_then_insert_successful(self):
        tester_name = "Tester"
        manager = self._setup_manager()
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        manager.add_player(manager.PARTICIPANTS, mock_player)
        updated_participants = manager.get_standard_teams()[0]
        self.assert_in_team(mock_player, updated_participants)

    def test_add_player_given_participants_full_when_player_added_to_participants_then_inserted_to_queue(self):
        min_size, max_size, team_count = 3, 3, 2
        manager = self._setup_manager(min_size, max_size, team_count)
        for i in range(max_size * team_count):
            mock_user = self._create_mock_user()
            manager.add_player(manager.PARTICIPANTS, mock_user)
        mock_player = self._create_mock_user()
        mock_player.id = self.id_generator.generate_viable_id()
        manager.add_player(manager.PARTICIPANTS, mock_player)
        updated_queue = manager.get_standard_teams()[2]
        self.assert_in_team(mock_player, updated_queue)

    def test_add_player_when_added_to_spectators_then_insert_successful(self):
        manager = self._setup_manager()
        mock_player = self._create_mock_user()
        mock_player.id = self.id_generator.generate_viable_id()
        manager.add_player(manager.SPECTATORS, mock_player)
        updated_participants = manager.get_standard_teams()[1]
        self.assert_in_team(mock_player, updated_participants)

    def test_add_player_when_player_in_a_team_already_then_invalid_join_raised(self):
        manager = self._setup_manager()
        mock_player = self._create_mock_user()
        mock_player.id = self.id_generator.generate_viable_id()
        expected_exception = BotInvalidJoinException(mock_player, manager.get_standard_teams()[0],
                                                     f"already a member of the team "
                                                     f"'{manager.get_standard_teams()[1].name}'")
        manager.add_player(manager.SPECTATORS, mock_player)
        self._assert_raises_correct_exception(expected_exception, manager.add_player, manager.PARTICIPANTS, mock_player)

    def test_add_player_given_team_not_full_when_added_to_game_teams_with_team_name_then_insert_successful(self):
        min_size, max_size, team_count = 6, 6, 5
        manager = self._setup_manager(min_size, max_size, team_count)
        for team in range(team_count):
            with self.subTest(f"Adding player to game team with team name (Team {team + 1})"):
                mock_player = MagicMock()
                mock_player.id = self.id_generator.generate_viable_id()
                manager.add_player(f"Team {team + 1}", mock_player)
                updated_participants = manager.get_game_teams()[team]
                self.assert_in_team(mock_player, updated_participants)

    def test_add_player_given_team_not_full_when_added_to_game_teams_with_team_number_then_insert_successful(self):
        min_size, max_size, team_count = 1, 3, 4
        manager = self._setup_manager(min_size, max_size, team_count)
        for team in range(team_count):
            with self.subTest(f"Adding player to game team with team number (Team {team + 1})"):
                mock_player = self._create_mock_user()
                manager.add_player(team, mock_player)
                updated_participants = manager.get_game_teams()[team]
                self.assert_in_team(mock_player, updated_participants)

    def test_add_player_given_team_full_when_added_to_game_team_then_error_raised(self):
        min_size, max_size, team_count = 1, 5, 4
        manager = self._setup_manager(min_size, max_size, team_count)
        self._fill_teams(manager, max_size, team_count)
        mock_player = self._create_mock_user()
        for team in range(team_count):
            with self.subTest(f"Adding player to full game team (Team {team + 1})"):
                expected_exception = BotInvalidJoinException(mock_player, manager.get_game_teams()[team],
                                                             "Could not add a player into a full team.")
                self._assert_raises_correct_exception(expected_exception, manager.add_player, team, mock_player)

    def test_has_enough_participants_given_no_participants_then_false_returned(self):
        manager = self._setup_manager()
        self.assertFalse(manager.has_enough_participants)

    def test_has_enough_participants_given_participants_under_min_team_size_times_team_count_then_false_returned(self):
        min_size, max_size, team_count = 2, 2, 8
        manager = self._setup_manager(min_size, max_size, team_count)
        for _ in range(min_size*team_count - 1):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        self.assertFalse(manager.has_enough_participants)

    def test_has_enough_participants_given_participants_at_min_team_size_times_team_count_then_true_returned(self):
        min_size, max_size, team_count = 4, 8, 2
        manager = self._setup_manager(min_size, max_size, team_count)
        for _ in range(min_size * team_count):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        self.assertTrue(manager.has_enough_participants)

    def test_has_enough_participants_given_participants_at_max_team_size_times_team_count_then_true_returned(self):
        min_size, max_size, team_count = 5, 9, 5
        manager = self._setup_manager(min_size, max_size, team_count)
        for _ in range(max_size * team_count):
            manager.add_player(manager.PARTICIPANTS, self._create_mock_user())
        self.assertTrue(manager.has_enough_participants)

    def test_remove_player_given_valid_standard_team_when_called_with_player_in_team_then_player_removed(self):
        manager = self._setup_manager()
        mock_player = self._create_mock_user()
        for index, team in enumerate([manager.PARTICIPANTS, manager.SPECTATORS, manager.QUEUE]):
            with self.subTest(f"Remove player from standard team ({team})"):
                manager.add_player(team, mock_player)
                manager.remove_player(team, mock_player)
                standard_teams = manager.get_standard_teams()
                self.assertNotIn(mock_player, standard_teams[index].members)

    def test_remove_player_given_valid_game_team_when_called_with_player_in_team_then_player_removed(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        mock_player = self._create_mock_user()
        for team in range(team_count):
            with self.subTest(f"Remove player from team with team name (Team {team + 1})"):
                manager.add_player(team, mock_player)
                manager.remove_player(team, mock_player)
                game_teams = manager.get_game_teams()
                self.assertNotIn(mock_player, game_teams[team].members)

    def test_remove_player_given_valid_team_when_called_with_player_not_in_team_then_error_raised(self):
        manager = self._setup_manager()
        mock_player = self._create_mock_user()
        expected_exception = BotInvalidPlayerRemoval(mock_player, manager.get_game_teams()[0])
        self._assert_raises_correct_exception(expected_exception, manager.remove_player, 0, mock_player)

    def test_remove_player_given_queue_has_players_when_removed_from_participants_then_filled_from_queue(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        mock_player = self._create_mock_user()
        for _ in range(max_size*team_count - 1):
            manager.add_player(manager.PARTICIPANTS, self._create_mock_user())
        manager.add_player(manager.PARTICIPANTS, mock_player)
        manager.add_player(manager.QUEUE, self._create_mock_user())
        manager.remove_player(manager.PARTICIPANTS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(max_size*team_count, len(standard_teams[0].members))
        self.assertEqual(0, len(standard_teams[2].members))

    def test_set_team_given_valid_move_then_player_removed_from_original_team_and_added_to_new_team(self):
        manager = self._setup_manager()
        mock_player = self._create_mock_user()
        manager.add_player(manager.PARTICIPANTS, mock_player)
        manager.set_team(manager.SPECTATORS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(0, len(standard_teams[0].members))
        self.assertEqual(1, len(standard_teams[1].members))

    def test_set_team_given_valid_move_when_moved_from_full_participants_and_queue_has_people_then_filled(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        mock_player = MagicMock()
        for _ in range(max_size * team_count - 1):
            manager.add_player(manager.PARTICIPANTS, self._create_mock_user())
        manager.add_player(manager.PARTICIPANTS, mock_player)
        manager.add_player(manager.QUEUE, MagicMock())
        manager.set_team(manager.SPECTATORS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(max_size * team_count, len(standard_teams[0].members))
        self.assertEqual(0, len(standard_teams[2].members))

    def test_set_team_given_player_not_in_any_team_then_error_raised(self):
        manager = self._setup_manager()
        player_name = "Invalid player"
        mock_player = self._create_mock_user()
        mock_player.display_name = player_name
        expected_exception = BotInvalidPlayerRemoval(mock_player, manager.get_standard_teams()[1])
        self._assert_raises_correct_exception(expected_exception, manager.set_team, manager.SPECTATORS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(0, len(standard_teams[0].members))

    def test_set_team_given_team_full_then_error_raised(self):
        manager = self._setup_manager()
        mock_player = self._create_mock_user()
        manager.add_player(manager.PARTICIPANTS, mock_player)
        for _ in range(5):
            manager.add_player(0, MagicMock())
        expected_exception = BotInvalidJoinException(mock_player, manager.get_game_teams()[0],
                                                     "Could not add a player into a full team.")
        self._assert_raises_correct_exception(expected_exception, manager.set_team, 0, mock_player)

    def test_clear_queue_given_players_in_queue_then_all_players_removed(self):
        manager = self._setup_manager()
        manager.add_player(manager.QUEUE, self._create_mock_user())
        manager.clear_queue()
        self.assertEqual(0, len(manager.get_standard_teams()[2].members))

    def test_clear_queue_given_no_players_in_queue_then_nothing_happens(self):
        manager = self._setup_manager()
        manager.clear_queue()
        self.assertEqual(0, len(manager.get_standard_teams()[2].members))

    def test_has_full_teams_when_min_team_sizes_met_then_returns_true(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        for team in range(team_count):
            for player in range(min_size):
                manager.add_player(team, self._create_mock_user())
        self.assertTrue(manager.has_full_teams)

    def test_has_full_teams_when_max_team_sizes_met_then_returns_true(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        for team in range(team_count):
            for player in range(max_size):
                manager.add_player(team, self._create_mock_user())
        self.assertTrue(manager.has_full_teams)

    def test_has_full_teams_when_all_min_team_sizes_not_met_then_returns_false(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        for team in range(team_count):
            for player in range(min_size-1):
                manager.add_player(team, self._create_mock_user())
        self.assertFalse(manager.has_full_teams)

    def test_has_participants_when_participants_present_returns_true(self):
        manager = self._setup_manager()
        manager.add_player(manager.PARTICIPANTS, MagicMock())
        self.assertTrue(manager.has_participants)

    def test_has_participants_when_no_participants_present_returns_false(self):
        manager = self._setup_manager()
        self.assertFalse(manager.has_participants)

    def test_all_players_in_voice_chat_when_all_players_are_in_voice_chat_returns_true(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        mock_participant = AsyncMock()
        self.participant_manager.try_get_participant.return_value = mock_participant
        mock_participant.voice = mock_voice_state
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        self.assertTrue(manager.all_players_in_voice_chat)

    def test_all_players_in_voice_chat_when_one_player_not_in_voice_chat_returns_false(self):
        min_size, max_size, team_count = 5, 6, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        player_not_in_voice = MagicMock()
        player_not_in_voice.user_id = self.id_generator.generate_viable_id()
        self.mocked_voice_states[player_not_in_voice.user_id] = player_not_in_voice
        manager.add_player(0, player_not_in_voice)
        self.assertFalse(manager.all_players_in_voice_chat)

    def test_all_players_in_voice_chat_when_one_player_in_wrong_voice_chat_returns_false(self):
        min_size, max_size, team_count = 5, 7, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        invalid_player = self._create_mock_player_with_voice_state(
            generate_mock_voice_state(self.id_generator.generate_viable_id()))
        manager.add_player(0, invalid_player)
        self.assertFalse(manager.all_players_in_voice_chat)

    def test_all_players_in_voice_chat_when_no_team_voice_channel_then_returns_false(self):
        min_size, max_size, team_count = 5, 7, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager.get_game_teams()[0].voice_channel = None
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, MagicMock())
        manager._participant_manager = self.participant_manager
        self.assertFalse(manager.all_players_in_voice_chat)

    def test_supports_voice_when_enough_channels_present_then_true(self):
        mock_game = _create_mock_game(5, 5, 3)
        teams_channels = [MagicMock()] * 3
        manager = ScrimTeamsManager(mock_game, team_channels=teams_channels)
        self.assertTrue(manager.supports_voice)

    def test_supports_voice_when_not_enough_channels_present_then_false(self):
        mock_game = _create_mock_game(5, 5, 3)
        manager = ScrimTeamsManager(mock_game)
        self.assertFalse(manager.supports_voice)

    def test_all_players_given_players_in_all_teams_returns_all_players(self):
        min_size, max_size, team_count = 3, 5, 6
        added_players = []
        manager = self._setup_manager(min_size, max_size, team_count)
        for team in range(team_count):
            for player in range(max_size):
                mock_user = self._create_mock_user()
                added_players.append(mock_user)
                manager.add_player(team, mock_user)
        self.assertEqual(len(manager.all_participants), len(added_players))
        for user in added_players:
            self.assertIn(user, manager.all_participants)

    async def test_try_move_to_voice_when_all_players_present_then_all_players_moved_to_their_teams_voice_channel(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._channel_provider = self.channel_provider
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        mock_voice_channel = MagicMock()
        self.channel_provider.get_channel.return_value = mock_voice_channel
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        self.assertTrue(await manager.try_move_to_voice())
        for team in manager.get_game_teams():
            for player in team.members:
                self.mocked_voice_states[player.user_id].move_to.assert_called_with(mock_voice_channel,
                                                                                    reason="Setting up a scrim.")

    async def test_try_move_to_voice_when_one_player_not_in_voice_chat_returns_false(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._channel_provider = self.channel_provider
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        skipped = False
        for team in range(team_count):
            for _ in range(min_size):
                if not skipped:
                    skipped = True
                    manager.add_player(team, self._create_mock_player_with_voice_state(None))
                    continue
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        self.assertFalse(await manager.try_move_to_voice())

    async def test_try_move_to_voice_when_one_player_in_wrong_voice_chat_returns_false(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._channel_provider = self.channel_provider
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        mock_invalid_voice_state = generate_mock_voice_state(self.id_generator.generate_nonviable_id())
        skipped = False
        for team in range(team_count):
            for _ in range(min_size):
                if not skipped:
                    skipped = True
                    manager.add_player(team, self._create_mock_player_with_voice_state(mock_invalid_voice_state))
                    continue
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        self.assertFalse(await manager.try_move_to_voice())

    async def test_move_to_lobby_given_lobby_exists_and_all_players_in_voice_then_all_players_moved_to_lobby(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice_and_lobby(max_size, min_size, team_count, mock_guild)
        manager._channel_provider = self.channel_provider
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        mock_voice_channel = MagicMock()
        self.channel_provider.get_channel.return_value = mock_voice_channel
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        await manager.move_to_lobby()
        for team in manager.get_game_teams():
            for player in team.members:
                self.mocked_voice_states[player.user_id].move_to.assert_called_with(mock_voice_channel,
                                                                                    reason="Ending a scrim.")

    async def test_move_to_lobby_given_no_lobby_channel_then_nobody_moved(self):
        min_size, max_size, team_count = 5, 5, 3
        mock_guild = self._create_mock_guild()
        manager = self._setup_mock_game_with_voice(max_size, min_size, team_count, mock_guild)
        manager._channel_provider = self.channel_provider
        manager._participant_manager = self.participant_manager
        mock_voice_state = generate_mock_voice_state(mock_guild.id)
        mock_voice_channel = MagicMock()
        self.channel_provider.get_channel.return_value = mock_voice_channel
        for team in range(team_count):
            for _ in range(min_size):
                manager.add_player(team, self._create_mock_player_with_voice_state(mock_voice_state))
        await manager.move_to_lobby()
        for team in manager.get_game_teams():
            for player in team.members:
                self.mocked_voice_states[player.user_id].move_to.assert_not_called()

    def test_clear_teams_given_all_players_in_game_teams_then_all_players_moved_to_participants(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        players = []
        for team in range(team_count):
            for player in range(max_size):
                mock_user = self._create_mock_user()
                players.append(mock_user)
                manager.add_player(team, mock_user)
        manager.clear_teams()
        for player in players:
            self.assertIn(player, manager.get_standard_teams()[0].members)

    def test_clear_teams_given_some_players_in_teams_then_all_players_moved_to_participants_and_no_errors_raised(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = self._setup_manager(min_size, max_size, team_count)
        iterations = 10
        for iteration in range(1, iterations + 1):
            with self.subTest(f"Testing team clearing with random amount of players in team (iteration {iteration} "
                              f"out of {iterations})"):
                for team in manager._teams.values():
                    team.members.clear()
                players = []
                for team in range(team_count):
                    for player in range(max_size):
                        mock_user = self._create_mock_user()
                        players.append(mock_user)
                        if random.random() > 0.5:
                            manager.add_player(team, mock_user)
                        else:
                            manager.add_player(manager.PARTICIPANTS, mock_user)
                manager.clear_teams()
                for player in players:
                    self.assertIn(player, manager.get_standard_teams()[0].members)

    def _create_mock_guild(self):
        guild_id = self.id_generator.generate_viable_id()
        mock_guild = MagicMock()
        mock_guild.id = guild_id
        return mock_guild

    def _setup_manager(self, min_size=5, max_size=5, team_count=2):
        mock_game = _create_mock_game(min_size, max_size, team_count)
        return ScrimTeamsManager(mock_game, self.participant_manager)

    def _setup_mock_game_with_voice(self, max_size, min_size, team_count, mock_guild):
        mock_game = _create_mock_game(min_size, max_size, team_count)
        channel_ids = self.id_generator.generate_viable_id_group(team_count)
        teams_channels = [generate_mock_voice_channel(channel_id, guild=mock_guild) for channel_id in channel_ids]
        manager = ScrimTeamsManager(mock_game, team_channels=teams_channels)
        return manager

    def _setup_mock_game_with_voice_and_lobby(self, max_size, min_size, team_count, mock_guild):
        mock_game = _create_mock_game(min_size, max_size, team_count)
        channel_ids = self.id_generator.generate_viable_id_group(team_count)
        teams_channels = [generate_mock_voice_channel(channel_id, guild=mock_guild) for channel_id in channel_ids]
        lobby_channel = generate_mock_voice_channel(self.id_generator.generate_viable_id())
        manager = ScrimTeamsManager(mock_game, team_channels=teams_channels, lobby=lobby_channel)
        return manager

    def _assert_valid_standard_teams(self, standard_teams, max_size, min_size, team_count):
        for team_name in [ScrimTeamsManager.PARTICIPANTS, ScrimTeamsManager.SPECTATORS, ScrimTeamsManager.QUEUE]:
            self.assertIn(team_name, [team.name for team in standard_teams])
        self.assertEqual(min_size * team_count, standard_teams[0].min_size)
        self.assertEqual(max_size * team_count, standard_teams[0].min_size)
        self.assertEqual(0, standard_teams[1].min_size)
        self.assertEqual(0, standard_teams[1].max_size)
        self.assertEqual(0, standard_teams[2].min_size)
        self.assertEqual(0, standard_teams[2].max_size)

    def _assert_valid_game_teams(self, game_teams, max_size, min_size, team_count):
        self.assertEqual(team_count, len(game_teams))
        for team in game_teams:
            self.assertEqual(min_size, team.min_size)
            self.assertEqual(max_size, team.max_size)

    def assert_in_team(self, mock_player, team: Team):
        self.assertIn(mock_player, team.members)

    def _create_mock_user(self) -> User:
        return User(user_id=self.id_generator.generate_viable_id())

    def _fill_teams(self, manager, max_size, team_count):
        for team_index in range(team_count):
            for player_num in range(max_size):
                manager.add_player(team_index, self._create_mock_user())

    def _create_mock_player_with_voice_state(self, mock_voice_state):
        new_player = AsyncMock()
        new_player.id = self.id_generator.generate_viable_id()
        new_player.voice = mock_voice_state
        new_user = MagicMock()
        new_user.user_id = new_player.id
        self.mocked_voice_states[new_player.id] = new_player
        return new_user
