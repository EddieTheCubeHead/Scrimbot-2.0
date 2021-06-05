__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest

from Database.Exceptions.DatabaseBaseException import DatabaseBaseException


class TestDatabaseBaseException(unittest.TestCase):

    def test_get_message_given_valid_instance_then_returns_correct_message(self):
        test_exception = DatabaseBaseException("example_table", "example_field", "example_value")
        expected_message = "Raw database exception in table 'example_table', column 'example_field' with row value " \
                           "'example_value'"
        self.assertEqual(expected_message, test_exception.get_message())
