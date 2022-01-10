__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Test.Utils.TestBases.UnittestBase import UnittestBase
from Database.Exceptions.DatabasePrimaryKeyViolatedException import DatabasePrimaryKeyViolatedException


class TestDatabaseMissingRowException(UnittestBase):

    def test_get_message_given_valid_instance_with_single_column_pk_fields_then_returns_correct_message(self):
        test_exception = DatabasePrimaryKeyViolatedException("example_table", ["example_field"], ["example_value"])
        expected_message = "Primary key consisting of value example_value for column example_field already exists in " \
                           "table example_table"
        self.assertEqual(expected_message, test_exception.get_message())

    def test_get_message_given_valid_instance_with_double_column_pk_fields_then_returns_correct_message(self):
        test_exception = DatabasePrimaryKeyViolatedException("example_table", ["field1", "field2"], ["1", "2"])
        expected_message = "Primary key consisting of values 1 and 2 for columns field1 and field2 already exists in " \
                           "table example_table"
        self.assertEqual(expected_message, test_exception.get_message())

    def test_get_message_given_valid_instance_with_multiple_pk_fields_then_returns_correct_message(self):
        test_exception = DatabasePrimaryKeyViolatedException("example_table", ["f1", "f2", "f3"], ["1", "2", "3"])
        expected_message = "Primary key consisting of values 1, 2 and 3 for columns f1, f2 and f3 already exists in " \
                           "table example_table"
        self.assertEqual(expected_message, test_exception.get_message())
