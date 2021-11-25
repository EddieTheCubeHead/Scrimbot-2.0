__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.TestBases.UnittestBase import UnittestBase
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class TestBotBaseUserException(UnittestBase):

    def setUp(self) -> None:
        self.logger = MagicMock()

    def test_resolve_given_logging_enabled_then_warning_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=True)
        new_exception.resolve(ctx)
        self.logger.warning.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                               f"caused an unspecified exception with the following message:"
                                               f" '{error_message}'")

    def test_resolve_given_logging_disabled_then_nothing_happens(self):
        ctx = MagicMock()
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=False)
        new_exception.resolve(ctx)
        self.logger.warning.assert_not_called()

    def test_resolve_given_logging_not_specified_then_warning_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger)
        new_exception.resolve(ctx)
        self.logger.warning.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                               f"caused an unspecified exception with the following message:"
                                               f" '{error_message}'")
