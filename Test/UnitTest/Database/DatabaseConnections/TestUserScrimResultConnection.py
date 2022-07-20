__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.DataClasses.UserScrimResult import Result, UserScrimResult
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.UserScrimResultConnection import UserScrimResultConnection
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestUserScrimResultConnection(UnittestBase):

    config: Config = None
    master: MasterConnection = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()
        cls.config = MagicMock()
        cls.master = MasterConnection(cls.config, ":memory:")

    def setUp(self) -> None:
        self.connection: UserScrimResultConnection = UserScrimResultConnection(self.master)

    def test_create_result_when_called_with_correct_data_then_new_result_created(self):
        mock_user_id, mock_rating_id, mock_scrim_id = self.id_generator.generate_viable_id_group(3)
        mock_rating = 1777
        mock_result = Result.WIN
        self.connection.create_result(mock_user_id, mock_rating_id, mock_scrim_id, mock_rating, mock_result)
        with self.master.get_session() as session:
            actual_result = session.query(UserScrimResult).filter(UserScrimResult.user_id == mock_user_id)\
                .filter(UserScrimResult.rating_id == mock_rating_id).first()
        self.assertEqual(mock_user_id, actual_result.user_id)
        self.assertEqual(mock_rating_id, actual_result.rating_id)
        self.assertEqual(mock_scrim_id, actual_result.scrim_id)
        self.assertEqual(mock_rating, actual_result.frozen_rating)
        self.assertEqual(mock_result, actual_result.result)
