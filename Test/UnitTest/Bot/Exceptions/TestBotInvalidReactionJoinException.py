__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Exceptions.BotInvalidReactionJoinException import BotInvalidReactionJoinException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotInvalidReactionJoinException(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.reaction = AsyncMock()
        self.reaction.__str__.return_value = "Test reaction"
        self.user = MagicMock()
        self.user.id = self.id_generator.generate_viable_id()
        self.team = MagicMock()
        self.team.name = str(self.id_generator.generate_viable_id())
        self.reason = f"already a member of the team '{self.id_generator.generate_viable_id()}'"
        self.logger = MagicMock()
        self.exception = BotInvalidReactionJoinException(self.user, self.team, self.reaction, self.reason, self.logger)

    def test_init_given_reaction_user_team_and_reason_then_constructs_message_correctly(self):
        self.assertEqual(f"User '{self.user.id}' could not join team '{self.team.name}' with reaction "
                         f"{self.reaction} because they are {self.reason}.", self.exception.message)

    async def test_resolve_when_called_then_removes_reaction(self):
        await self.exception.resolve()
        self.reaction.remove.assert_called_with(self.user)

    async def test_resolve_when_called_then_debug_logged(self):
        await self.exception.resolve()
        self.logger.debug.assert_called_with(f"An exception occurred during bot operation: User '{self.user.id}' "
                                             f"could not join team '{self.team.name}' with reaction {self.reaction} "
                                             f"because they are {self.reason}.")
