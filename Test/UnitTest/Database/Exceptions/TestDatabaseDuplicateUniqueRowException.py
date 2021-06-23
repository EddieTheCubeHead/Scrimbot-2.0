__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Utils.UnittestBase import UnittestBase
from Database.Exceptions.DatabaseDuplicateUniqueRowException import DatabaseDuplicateUniqueRowException


class TestDatabaseDuplicateUniqueRowException(UnittestBase):

    def test_get_message_given_valid_instance_then_returns_correct_message(self):
        test_exception = DatabaseDuplicateUniqueRowException("example_table", "example_column", "example_value")
        expected_message = "A row with value 'example_value' for unique restraint column 'example_column' already " \
                           "exists in table 'example_table'"
        self.assertEqual(expected_message, test_exception.get_message())
