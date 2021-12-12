__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Utils.TestBases.UnittestBase import UnittestBase
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL


class TestBotBaseUserException(UnittestBase):

    def setUp(self) -> None:
        self.logger = MagicMock()

    def test_resolve_given_logging_disabled_then_nothing_happens(self):
        ctx = MagicMock()
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=NOTSET)
        new_exception.resolve(ctx)
        self.logger.debug.assert_not_called()
        self.logger.info.assert_not_called()
        self.logger.warning.assert_not_called()
        self.logger.error.assert_not_called()
        self.logger.critical.assert_not_called()

    def test_resolve_given_logging_level_debug_then_debug_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=DEBUG)
        new_exception.resolve(ctx)
        self.logger.debug.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                             f"caused an unspecified exception with the following message:"
                                             f" '{error_message}'")

    def test_resolve_given_logging_level_info_then_info_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=INFO)
        new_exception.resolve(ctx)
        self.logger.info.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                            f"caused an unspecified exception with the following message:"
                                            f" '{error_message}'")

    def test_resolve_given_logging_level_warning_then_warning_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=WARNING)
        new_exception.resolve(ctx)
        self.logger.warning.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                               f"caused an unspecified exception with the following message:"
                                               f" '{error_message}'")

    def test_resolve_given_logging_level_error_then_error_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=ERROR)
        new_exception.resolve(ctx)
        self.logger.error.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                             f"caused an unspecified exception with the following message:"
                                             f" '{error_message}'")

    def test_resolve_given_logging_level_critical_then_critical_logged(self):
        ctx = MagicMock()
        ctx.command.name = "test"
        ctx.message.content = ";test args"
        error_message = "Test error to be logged"
        new_exception = BotBaseInternalException(error_message, self.logger, log=CRITICAL)
        new_exception.resolve(ctx)
        self.logger.critical.assert_called_with(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                                f"caused an unspecified exception with the following message:"
                                                f" '{error_message}'")

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
