__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlalchemy.orm

from Utils.UnittestBase import UnittestBase
from Database.Core.MasterConnection import MasterConnection


class TestMasterConnection(UnittestBase):

    def setUp(self) -> None:
        self.db_address = ":memory:"
        self.connection = MasterConnection(self.db_address)

    def test_get_session_given_db_address_given_then_session_connected_to_db_recieved(self):
        session: sqlalchemy.orm.Session = self.connection.get_session()
        self.assertEqual(self.db_address, session.bind.engine.url.database)

