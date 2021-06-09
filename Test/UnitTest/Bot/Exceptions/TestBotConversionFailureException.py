__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from Bot.DataClasses.Scrim import Scrim
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException


class TestBotConversionFailureException(unittest.TestCase):

    def test_get_description_given_valid_exception_then_correct_message_constructed(self):
        argument = "Foo"
        conversion_type = "Scrim"
        new_exception = BotConversionFailureException(conversion_type, "Foo")
        self.assertEqual(f"Could not convert argument '{argument}' into type {conversion_type}",
                         new_exception.get_description())
