__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Exceptions.BotUnrecognizedCommandException import BotUnrecognizedCommandException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestBotUnrecognizedCommandException(AsyncUnittestBase):

    def test_init_given_faulty_context_then_new_exception_created_correctly(self):
        faulty_context = MagicMock()
        faulty_context.invoked_with = "faulty_command"
        exception = BotUnrecognizedCommandException(faulty_context)
        self.assertEqual("Could not recognize command 'faulty_command'", exception.message)
