__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from typing import Callable
from unittest.mock import MagicMock

from sqlalchemy.orm import subqueryload, joinedload

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.DataClasses.Team import Team, PARTICIPANTS, QUEUE, SPECTATORS
from Src.Bot.DataClasses.User import User
from Src.Bot.DataClasses.UserScrimResult import UserScrimResult, Result
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.ScrimConnection import ScrimConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


_RESULT_MAPPING: dict[int | None: Result] = {
    None: Result.UNREGISTERED,
    0: Result.TIE,
    1: Result.WIN,
    2: Result.LOSS
}


class TestScrimConnection(UnittestBase):

    config: Config
    master: MasterConnection
    test_game: Game

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = Config()
        cls.master = MasterConnection(cls.config, ":memory:")
        _test_game = Game("Test game", "colour", "icon", 5)
        with cls.master.get_session() as session:
            session.add(_test_game)

        with cls.master.get_session() as session:
            cls._test_game = session.query(Game).filter(Game.name == "Test game").first()

    def setUp(self) -> None:
        self.connection: ScrimConnection = ScrimConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimConnection)

    def test_add_scrim_given_valid_scrim_when_called_then_scrim_created(self):
        result_scrim = self._create_mock_scrim()
        added_scrim = self.connection.add_scrim(result_scrim)
        self._assert_scrim_in_database(added_scrim)

    def test_add_scrim_given_team_results_attached_then_user_scrim_results_created(self):
        result_scrim = self._create_mock_scrim()
        expected_results = self._create_win_results(result_scrim)
        actual_scrim = self.connection.add_scrim(result_scrim)
        for team in expected_results:
            self._assert_team_results_created(team, actual_scrim)

    def test_exists_given_scrim_on_channel_when_called_with_channel_id_then_returns_true(self):
        valid_states = [ScrimState.LFP, ScrimState.LOCKED, ScrimState.STARTED, ScrimState.VOICE_WAIT, ScrimState.CAPS,
                        ScrimState.CAPS_PREP]
        for state in valid_states:
            with self.subTest(f"exists returns true with state {state}"):
                expected_scrim = self._save_scrim(state)
            self.assertTrue(self.connection.exists(expected_scrim.channel_id))

    def test_exists_given_ended_scrim_on_channel_when_called_with_channel_id_then_returns_false(self):
        invalid_states = [ScrimState.ENDED, ScrimState.TERMINATED]
        for state in invalid_states:
            with self.subTest(f"exists returns false with state {state}"):
                expected_scrim = self._save_scrim(state)
            self.assertFalse(self.connection.exists(expected_scrim.channel_id))

    def test_get_active_scrim_when_fetched_with_channel_id_then_returns_the_active_scrim_on_channel(self):
        expected_scrim = self._save_scrim(ScrimState.LFP)
        self._assert_same_scrim(expected_scrim, self.connection.get_active_scrim(expected_scrim.channel_id))

    def test_edit_scrim_given_scrim_teams_changed_when_called_then_changes_saved(self):
        expected_scrim = self._save_scrim(ScrimState.LFP)
        mock_user = User(self.id_generator.generate_viable_id())
        participant_team = ParticipantTeam(None)
        team = Team(PARTICIPANTS)
        participant_team.team = team
        expected_scrim.teams.append(participant_team)
        expected_scrim.teams[0].team.members.append(mock_user)
        self.connection.edit_scrim(expected_scrim)
        self._assert_scrim_in_database(expected_scrim)

    def _create_mock_scrim(self, state: ScrimState = ScrimState.LFP):
        mock_message = MagicMock()
        mock_message.channel.id = self.id_generator.generate_viable_id()
        mock_message.id = self.id_generator.generate_viable_id()
        result_scrim = Scrim(mock_message, self._test_game, state)
        return result_scrim

    def _assert_scrim_in_database(self, scrim: Scrim):
        with self.master.get_session() as session:
            actual = session.query(Scrim).filter(Scrim.scrim_id == scrim.scrim_id).one()
            self._assert_equal_scrim(scrim, actual)

    def _assert_equal_scrim(self, expected: Scrim, actual: Scrim):
        self.assertEqual(expected.scrim_id, actual.scrim_id)
        self.assertEqual(expected.channel_id, actual.channel_id)
        self.assertEqual(expected.game_name, actual.game_name)
        self.assertEqual(len(expected.teams), len(actual.teams))
        for expected_team, actual_team in zip(expected.teams, actual.teams):
            self.assertEqual(expected_team.placement, actual_team.placement)
            self.assertEqual(expected_team.team.name, actual_team.team.name)
            self.assertEqual(len(expected_team.team.members), len(actual_team.team.members))

    def _create_win_results(self, scrim: Scrim, team_amount: int = 2, team_size: int = 5):
        result_teams = []
        for placement in range(1, team_amount + 1):
            participant_team = self._create_participant_team(scrim.scrim_id, placement, team_size)
            team = Team(f"Team {placement}")
            participant_team.team = team
            result_teams.append(participant_team)
        return result_teams

    def _create_tie_results(self, scrim: Scrim, team_amount: int = 2, team_size: int = 5):
        for placement in range(1, team_amount + 1):
            participant_team = self._create_participant_team(scrim.scrim_id, 0, team_size)
            team = Team(f"Team {placement}")
            participant_team.team = team
            scrim.teams.append(participant_team)

    def _create_unregistered_results(self, scrim: Scrim, team_amount: int = 2, team_size: int = 5):
        for placement in range(1, team_amount + 1):
            participant_team = self._create_participant_team(scrim.scrim_id, None, team_size)
            team = Team(f"Team {placement}")
            participant_team.team = team
            scrim.teams.append(participant_team)

    def _create_participant_team(self, scrim_id: int, placement: int | None, team_size: int = 5) -> ParticipantTeam:
        team = self._create_team(team_size)
        participant_team = ParticipantTeam(placement, self._test_game.max_team_size, self._test_game.min_team_size)
        for player in team.members:
            player_result = UserScrimResult(None, player.user_id, scrim_id, 1700, _RESULT_MAPPING[placement])
            player.results.append(player_result)
        participant_team.team = team
        return participant_team

    def _create_team(self, size: int = 5) -> Team:
        players = [User(self.id_generator.generate_viable_id()) for _ in range(size)]
        return Team(str(self.id_generator.generate_viable_id()), players, size, size)

    def _assert_team_results_created(self, team: ParticipantTeam, scrim: Scrim):
        for member in team.team.members:
            member_result = self._assert_player_has_result(member, scrim.scrim_id)
            self.assertEqual(_RESULT_MAPPING[team.placement], member_result.result)

    def _assert_player_has_result(self, member: User, scrim_id: int) -> UserScrimResult:
        with self.master.get_session() as session:
            result = session.query(UserScrimResult).filter(UserScrimResult.user_id == member.user_id)\
                .filter(UserScrimResult.scrim_id == scrim_id).first()
        self.assertIsNotNone(result)
        return result

    def _save_scrim(self, state: ScrimState):
        mock_scrim = self._create_mock_scrim(state)
        channel = ScrimChannel(mock_scrim.channel_id, self.id_generator.generate_viable_id())
        with self.master.get_session() as session:
            session.add(mock_scrim)
            session.add(channel)
            mock_scrim.scrim_channel = channel
            pass
        return mock_scrim

    def _assert_same_scrim(self, expected_scrim: Scrim, actual_scrim: Scrim):
        self.assertEqual(expected_scrim.scrim_id, actual_scrim.scrim_id)
        self.assertEqual(expected_scrim.channel_id, actual_scrim.channel_id)
        self.assertEqual(expected_scrim.game.name, actual_scrim.game.name)
        self.assertEqual(expected_scrim.state, actual_scrim.state)
        for expected_team, actual_team in zip(expected_scrim.teams, actual_scrim.teams):
            self._assert_equal_team(expected_team, actual_team)
        self._assert_same_channel(expected_scrim.scrim_channel, actual_scrim.scrim_channel)

    def _assert_equal_team(self, expected_team: ParticipantTeam, actual_team: ParticipantTeam):
        self.assertEqual(expected_team.team.name, actual_team.team.name)
        self.assertEqual(expected_team.team_id, actual_team.team_id)
        self.assertEqual(expected_team.scrim_id, actual_team.scrim_id)
        self.assertEqual(len(expected_team.team.members), actual_team.team.members)

    def _assert_same_channel(self, expected_channel: ScrimChannel, actual_channel: ScrimChannel):
        if expected_channel is None:
            self.assertIsNone(actual_channel)
            return
        self.assertEqual(expected_channel.channel_id, actual_channel.channel_id)
        for expected_voice, actual_voice in zip(expected_channel.voice_channels, actual_channel.voice_channels):
            self.assertEqual(expected_voice.channel_id, actual_voice.channel_id)

