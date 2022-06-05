__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.User import User
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

    def _assert_user_in_database(self, user_id):
        with self.master.get_session() as session:
            session.query(User).filter(User.user_id == user_id).one()
