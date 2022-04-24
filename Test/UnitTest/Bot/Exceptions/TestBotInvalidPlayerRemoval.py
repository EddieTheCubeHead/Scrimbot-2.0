__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG
from unittest.mock import AsyncMock, MagicMock

from Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Test.Utils.TestBases.UnittestBase import UnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotInvalidPlayerRemoval(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def test_init_given_text_channel_tells_channel_reserved_for_scrim_already(self):
        logger = MagicMock()
        player = MagicMock()
        player.user_id = self.id_generator.generate_viable_id()
        team = MagicMock()
        team.name = "TeamTest"
        exception = BotInvalidPlayerRemoval(player, team, logger)
        self.assertEqual(f"Tried to remove player <@{player.user_id}> from team 'TeamTest' even though they are not a "
                         f"team member.", exception.message)

    def test_init_given_called_then_logging_level_debug_set(self):
        player = MagicMock()
        team = MagicMock()
        team.name = "TeamTest"
        exception = BotInvalidPlayerRemoval(player, team, MagicMock())
        self.assertEqual(DEBUG, exception.log)
