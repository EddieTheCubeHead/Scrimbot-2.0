__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Test.Utils.TestBases.UnittestBase import UnittestBase
from Src.Database.Core.MasterConnection import MasterConnection


class TestMasterConnection(UnittestBase):

    def setUp(self) -> None:
        self.db_address = ":memory:"
        self.config = MagicMock()
        self.connection = MasterConnection(self.config, self.db_address)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(MasterConnection)

    def test_get_session_given_session_exists_given_db_address_given_then_session_connected_to_db_received(self):
        self.assertEqual(self.db_address, self.connection.session().bind.engine.url.database)

