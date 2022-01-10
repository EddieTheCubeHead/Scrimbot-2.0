__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Test.Utils.TestBases.UnittestBase import UnittestBase
from Database.Exceptions.DatabaseMissingRowException import DatabaseMissingRowException


class TestDatabaseMissingRowException(UnittestBase):

    def test_get_message_given_valid_instance_then_returns_correct_message(self):
        test_exception = DatabaseMissingRowException("example_table", "example_field", "example_value")
        expected_message = "Did not find a row with value 'example_value' for column 'example_field' in table " \
                           "'example_table'"
        self.assertEqual(expected_message, test_exception.get_message())
