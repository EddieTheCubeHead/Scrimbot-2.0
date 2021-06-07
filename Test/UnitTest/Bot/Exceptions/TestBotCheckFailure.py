__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest

from Bot.Exceptions.BotCheckFailure import BotCheckFailure


class TestBotCheckFailure(unittest.TestCase):

    def test_get_header_given_valid_exception_then_correct_string_returned(self):
        new_exception = BotCheckFailure("Foo")
        self.assertEqual("Check failed:", new_exception.get_header())
