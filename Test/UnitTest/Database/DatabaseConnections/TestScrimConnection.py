__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from sqlalchemy.orm import subqueryload, joinedload

from Bot.DataClasses.Game import Game
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.ScrimConnection import ScrimConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimConnection(UnittestBase):

    config: Config

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = Config()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection: ScrimConnection = ScrimConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimConnection)

    def test_add_channel_given_valid_channel_then_channel_and_voices_successfully_added(self):
        result_scrim = self._create_mock_scrim()
        added_scrim = self.connection.add_scrim(result_scrim)
        self._assert_scrim_in_database(added_scrim)

    def _create_mock_scrim(self, team_amount: int = 2):
        mock_manager = MagicMock()
        mock_manager.message.channel.id = self.id_generator.generate_viable_id()
        mock_manager.teams_manager.game = Game("Test game", "colour", "icon", 5)
        result_scrim = Scrim(mock_manager)
        for placement in range(1, team_amount + 1):
            participant_team = ParticipantTeam(placement)
            team = Team(f"Team {placement}")
            participant_team.team = team
            result_scrim.teams.append(participant_team)
        return result_scrim

    def _assert_scrim_in_database(self, scrim: Scrim):
        with self.master.get_session() as session:
            actual = session.query(Scrim).filter(Scrim.scrim_id == Scrim.scrim_id).one()
            self._assert_equal_scrim(scrim, actual)

    def _assert_equal_scrim(self, expected: Scrim, actual: Scrim):
        self.assertEqual(expected.scrim_id, actual.scrim_id)
        self.assertEqual(expected.channel_id, actual.channel_id)
        self.assertEqual(expected.game_name, actual.game_name)
        self.assertEqual(len(expected.teams), len(actual.teams))
        for expected_team, actual_team in zip(expected.teams, actual.teams):
            self.assertEqual(expected_team.placement, actual_team.placement)
            self.assertEqual(expected_team.team.name, actual_team.team.name)
