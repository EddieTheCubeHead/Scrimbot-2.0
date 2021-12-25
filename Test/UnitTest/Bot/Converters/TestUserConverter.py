__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.UserConverter import UserConverter
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestUserConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.context = MagicMock()
        self.converter = UserConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(UserConverter)

    def test_convert_given_called_user_id_then_user_returned(self):
        mock_user = MagicMock()
        mock_user.id = self.id_mocker.generate_viable_id()
        self.connection.get_user.return_value = mock_user
        actual_user = self.converter.convert(self.context, str(mock_user.id))
        self.assertEqual(mock_user, actual_user)
        self.connection.get_user.assert_called_with(mock_user.id)

    def test_get_user_given_called_with_user_id_then_user_returned(self):
        mock_user = MagicMock()
        mock_user.id = self.id_mocker.generate_viable_id()
        self.connection.get_user.return_value = mock_user
        actual_user = self.converter.get_user(mock_user.id)
        self.assertEqual(mock_user, actual_user)
        self.connection.get_user.assert_called_with(mock_user.id)
