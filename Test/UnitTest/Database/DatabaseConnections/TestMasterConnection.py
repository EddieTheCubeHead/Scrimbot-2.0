__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Utils.UnittestBase import UnittestBase
from Database.DatabaseConnections.MasterConnection import MasterConnection


class TestMasterConnection(UnittestBase):

    def setUp(self) -> None:
        self.db_path = ":memory:"
        self.connection = MasterConnection(self.db_path)

    def test_init_given_valid_path_then_connection_created(self):
        pass
