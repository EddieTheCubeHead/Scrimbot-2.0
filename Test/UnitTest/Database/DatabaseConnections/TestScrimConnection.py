__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Callable
from unittest.mock import MagicMock

from sqlalchemy.orm import subqueryload, joinedload

from Bot.DataClasses.Game import Game
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.DataClasses.UserScrimResult import UserScrimResult, Result
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

    def _create_mock_scrim(self):
        mock_manager = MagicMock()
        mock_manager.message.channel.id = self.id_generator.generate_viable_id()
        mock_manager.teams_manager.game = self._test_game
        result_scrim = Scrim(mock_manager)
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
        participant_team = ParticipantTeam(placement)
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
