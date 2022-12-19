__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.DataClasses.UserScrimResult import Result, UserScrimResult
from Src.Configs.Config import Config
from Src.Database.Core.MasterConnection import MasterConnection
from Src.Database.DatabaseConnections.UserScrimResultConnection import UserScrimResultConnection
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
        mock_rating = self._create_mock_rating()
        mock_scrim = self._create_mock_scrim()
        mock_result = Result.WIN
        self.connection.create_result(mock_rating, mock_scrim, mock_result)
        with self.master.get_session() as session:
            actual_result = session.query(UserScrimResult).filter(UserScrimResult.user_id == mock_rating.user_id)\
                .filter(UserScrimResult.rating_id == mock_rating.rating_id).first()
        self.assertEqual(mock_rating.user_id, actual_result.user_id)
        self.assertEqual(mock_rating.rating_id, actual_result.rating_id)
        self.assertEqual(mock_scrim.scrim_id, actual_result.scrim_id)
        self.assertEqual(mock_rating.rating, actual_result.frozen_rating)
        self.assertEqual(mock_result, actual_result.result)

    def _create_mock_rating(self, rating: int = 1700) -> UserRating:
        mock_rating = MagicMock()
        mock_rating.user_id = self.id_generator.generate_viable_id()
        mock_rating.rating_id = self.id_generator.generate_viable_id()
        mock_rating.rating = rating
        return mock_rating

    def _create_mock_scrim(self):
        mock_scrim = MagicMock()
        mock_scrim.scrim_id = self.id_generator.generate_viable_id()
        return mock_scrim
