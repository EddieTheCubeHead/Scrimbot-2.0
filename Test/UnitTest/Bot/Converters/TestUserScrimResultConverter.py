__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.UserScrimResultConverter import UserScrimResultConverter
from Utils.TestBases.UnittestBase import UnittestBase


class TestUserScrimResultConverter(UnittestBase):

    def setUp(self) -> None:
        self.mock_connection = MagicMock()
        self.converter = UserScrimResultConverter(self.mock_connection)

    def test_create_result_given_user_rating_and_scrim_then_result_with_frozen_rating_created(self):
        mock_user_rating = MagicMock()
        mock_scrim = MagicMock()
        mock_result = MagicMock()
        expected = MagicMock()
        self.mock_connection.create_result.return_value = expected
        actual = self.converter.create_result(mock_user_rating, mock_scrim, mock_result)
        self.mock_connection.create_result.assert_called_with(mock_user_rating.rating_id, mock_user_rating.user_id,
                                                              mock_scrim.scrim_id, mock_user_rating.rating, mock_result)
        self.assertEqual(actual, expected)
