__version__ = "0.2"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Cogs.Helpers.ScrimTeamOperationService import ScrimTeamOperationService
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import PARTICIPANTS, SPECTATORS, QUEUE
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


def _create_mock_teams(*team_names: str) -> [ParticipantTeam]:
    teams = []
    for team_name in team_names:
        mock_participant_team = MagicMock()
        mock_team = MagicMock()
        mock_team.members = []
        mock_team.name = team_name
        mock_participant_team.max_size = 0
        mock_participant_team.team = mock_team
        teams.append(mock_participant_team)
    return teams


class TestScrimTeamOperationService(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.service = ScrimTeamOperationService()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimTeamOperationService)

    def test_add_to_team_when_called_then_player_appended_to_correct_team(self):
        mock_scrim = self._create_mock_scrim()
        team_names = (PARTICIPANTS, SPECTATORS, QUEUE)
        mock_scrim.teams = _create_mock_teams(*team_names)
        mock_user = self._create_mock_user()
        for index, team_name in enumerate(team_names):
            with self.subTest(f"Adding player to team ({team_name})"):
                self.service.add_to_team(mock_scrim, mock_user, team_name)
                self.assertEqual(1, len(mock_scrim.teams[index].team.members))
                self.assertEqual(mock_user, mock_scrim.teams[index].team.members[0])

    def test_add_to_team_when_participants_full_then_player_appended_to_queue(self):
        mock_scrim = self._create_mock_scrim()
        team_names = (PARTICIPANTS, SPECTATORS, QUEUE)
        mock_scrim.teams = _create_mock_teams(*team_names)
        mock_user = self._create_mock_user()
        mock_scrim.teams[0].max_size = 10
        mock_scrim.teams[0].team.members = [MagicMock()] * 10
        self.service.add_to_team(mock_scrim, mock_user, PARTICIPANTS)
        self.assertEqual(1, len(mock_scrim.teams[2].team.members))
        self.assertEqual(10, len(mock_scrim.teams[0].team.members))

    def test_remove_from_team_given_player_in_any_team_when_called_then_player_removed_from_the_team(self):
        mock_scrim = self._create_mock_scrim()
        mock_scrim.teams = _create_mock_teams(PARTICIPANTS, SPECTATORS, QUEUE)
        mock_user = self._create_mock_user()
        for index in range(3):
            with self.subTest(f"Removing player from team ({mock_scrim.teams[index].team.name})"):
                mock_scrim.teams[index].team.members.append(mock_user)
                self.service.remove_from_team(mock_scrim, mock_user)
                self.assertNotIn(mock_user, mock_scrim.teams[index].team.members)

    def test_remove_from_team_when_participant_removed_and_players_in_queue_then_participants_filled_from_queue(self):
        mock_scrim = self._create_mock_scrim()
        team_names = (PARTICIPANTS, SPECTATORS, QUEUE)
        mock_scrim.teams = _create_mock_teams(*team_names)
        mock_user = self._create_mock_user()
        mock_scrim.teams[0].max_size = 10
        mock_scrim.teams[0].team.members = [MagicMock()] * 9 + [mock_user]
        mock_scrim.teams[2].team.members = [MagicMock()]
        self.service.remove_from_team(mock_scrim, mock_user)
        self.assertEqual(0, len(mock_scrim.teams[2].team.members))
        self.assertEqual(10, len(mock_scrim.teams[0].team.members))
        self.assertNotIn(mock_user, mock_scrim.teams[2])

    def _create_mock_scrim(self) -> Scrim:
        scrim = MagicMock()
        scrim.channel_id = self.id_generator.generate_viable_id()
        return scrim

    def _create_mock_user(self):
        user = MagicMock()
        user.user_id = self.id_generator.generate_viable_id()
        return user
