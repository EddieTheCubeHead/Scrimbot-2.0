__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Test.Utils.TestBases.UnittestBase import UnittestBase
from Database.Exceptions.DatabaseForeignKeyViolatedException import DatabaseForeignKeyViolatedException


class TestDatabaseForeignKeyViolatedException(UnittestBase):

    def test_get_message_given_valid_instance_then_returns_correct_message(self):
        test_exception = DatabaseForeignKeyViolatedException("example_table", "example_column", "example_value",
                                                             "foreign_table", "foreign_column")
        expected_message = "Did not find a row in table 'foreign_table' column 'foreign_column' corresponding to " \
                           "a foreign key constraint with value 'example_value' for column 'example_column' in table " \
                           "'example_table'"
        self.assertEqual(expected_message, test_exception.get_message())
