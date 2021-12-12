__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG
from unittest.mock import AsyncMock, MagicMock

from Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Utils.TestBases.UnittestBase import UnittestBase


class TestBotInvalidPlayerRemoval(UnittestBase):

    def test_init_given_text_channel_tells_channel_reserved_for_scrim_already(self):
        context = MagicMock()
        logger = MagicMock()
        nickname_service = MagicMock()
        nickname_service.get_name = MagicMock()
        nickname_service.get_name.return_value = "Tester"
        player = MagicMock()
        team = MagicMock()
        team.name = "TeamTest"
        exception = BotInvalidPlayerRemoval(context, player, team, nickname_service, logger)
        self.assertEqual("Tried to remove player 'Tester' from team 'TeamTest' even though they are not a team member.",
                         exception.message)

    def test_init_given_called_then_logging_level_debug_set(self):
        context = MagicMock()
        player = MagicMock()
        team = MagicMock()
        team.name = "TeamTest"
        exception = BotInvalidPlayerRemoval(context, player, team, MagicMock(), MagicMock())
        self.assertEqual(DEBUG, exception.log)
