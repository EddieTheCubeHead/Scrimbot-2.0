__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team
from Src.Bot.DataClasses.User import User
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.UserConnection import UserConnection
from Test.Utils.TestBases.ConnectionUnittest import ConnectionUnittest
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimChannelConnection(ConnectionUnittest[User]):

    config: Config = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = Config()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection: UserConnection = UserConnection(self.master)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserConnection)

    def test_get_user_given_existing_id_then_user_returned(self):
        user_id = self.id_generator.generate_viable_id()
        mock_user = User(user_id)
        with self.master.get_session() as session:
            session.add(mock_user)
        actual = self.connection.get_user(user_id)
        self.assertEqual(user_id, actual.user_id)

    def test_get_user_given_user_does_not_exist_then_user_created_returned_and_inserted_to_database(self):
        new_user_id = self.id_generator.generate_viable_id()
        new_user = self.connection.get_user(new_user_id)
        self.assertEqual(new_user_id, new_user.user_id)
        self._assert_user_in_database(new_user_id)

    def test_is_in_scrim_given_user_has_participant_team_with_scrim_in_progress_then_true_returned(self):
        user_id = self.id_generator.generate_viable_id()
        mock_user = User(user_id)
        mock_game = Game(str(self.id_generator.generate_viable_id()), "0xffffff", "www.icon.example", 5)
        mock_participant_team = ParticipantTeam(None, mock_game.max_team_size, mock_game.min_team_size)
        mock_team = Team("Team 1")
        for state in (ScrimState.LFP, ScrimState.LOCKED, ScrimState.VOICE_WAIT, ScrimState.STARTED, ScrimState.CAPS,
                      ScrimState.CAPS_PREP):
            with self.subTest(f"Test is user in active scrim: ScrimState: {state}"):
                mock_message = MagicMock()
                mock_message.channel.id = self.id_generator.generate_viable_id()
                mock_message.id = self.id_generator.generate_viable_id()
                mock_scrim = Scrim(mock_message, mock_game, state)
                with self.master.get_session() as session:
                    session.add(mock_user)
                    session.add(mock_game)
                    session.add(mock_scrim)
                    mock_scrim.teams.append(mock_participant_team)
                    mock_participant_team.team = mock_team
                    mock_team.members.append(mock_user)
                self.assertTrue(self.connection.is_in_scrim(user_id))

    def test_is_in_scrim_given_user_has_participant_team_with_non_active_scrim_then_false_returned(self):
        user_id = self.id_generator.generate_viable_id()
        mock_user = User(user_id)
        mock_game = Game(str(self.id_generator.generate_viable_id()), "0xffffff", "www.icon.example", 5)
        mock_participant_team = ParticipantTeam(None, mock_game.max_team_size, mock_game.min_team_size)
        mock_team = Team("Team 1")
        for state in (ScrimState.ENDED, ScrimState.TERMINATED):
            with self.subTest(f"Test is user in active scrim: ScrimState: {state}"):
                mock_message = MagicMock()
                mock_message.channel.id = self.id_generator.generate_viable_id()
                mock_message.id = self.id_generator.generate_viable_id()
                mock_scrim = Scrim(mock_message, mock_game, state)
                with self.master.get_session() as session:
                    session.add(mock_user)
                    session.add(mock_game)
                    session.add(mock_scrim)
                    mock_scrim.teams.append(mock_participant_team)
                    mock_participant_team.team = mock_team
                    mock_team.members.append(mock_user)
                self.assertFalse(self.connection.is_in_scrim(user_id))

    def _assert_user_in_database(self, user_id):
        with self.master.get_session() as session:
            session.query(User).filter(User.user_id == user_id).one()
