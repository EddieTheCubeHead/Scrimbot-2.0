__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotInvalidJoinException(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.user = MagicMock()
        self.user.user_id = self.id_generator.generate_viable_id()
        self.team = MagicMock()
        self.team.name = str(self.id_generator.generate_viable_id())
        self.reason = f"already a member of the team '{self.id_generator.generate_viable_id()}'"
        self.logger = MagicMock()
        self.exception = BotInvalidJoinException(self.user, self.team, self.reason, self.logger)

    def test_init_given_reaction_user_team_and_reason_then_constructs_message_correctly(self):
        self.assertEqual(f"User '{self.user.user_id}' could not join team '{self.team.name}' because they are "
                         f"{self.reason}.", self.exception.message)

    def test_resolve_when_called_then_debug_logged(self):
        self.exception.resolve()
        self.logger.debug.assert_called_with(f"An exception occurred during bot operation: User '{self.user.user_id}' "
                                             f"could not join team '{self.team.name}' because they are {self.reason}.")
