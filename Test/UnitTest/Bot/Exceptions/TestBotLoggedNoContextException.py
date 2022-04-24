__version__ = "ver"
__author__ = "Eetu Asikainen"

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from unittest.mock import MagicMock

from Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException
from Test.Utils.TestBases.UnittestBase import UnittestBase


class TestBotLoggedNoContextException(UnittestBase):
    def setUp(self) -> None:
        self.logger = MagicMock()

    def test_resolve_given_logging_disabled_then_nothing_happens(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger, log=NOTSET)
        new_exception.resolve()
        self.logger.debug.assert_not_called()
        self.logger.info.assert_not_called()
        self.logger.warning.assert_not_called()
        self.logger.error.assert_not_called()
        self.logger.critical.assert_not_called()

    def test_resolve_given_logging_level_debug_then_debug_logged(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger, log=DEBUG)
        new_exception.resolve()
        self.logger.debug.assert_called_with(f"An exception occurred during bot operation: {error_message}")

    def test_resolve_given_logging_level_info_then_info_logged(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger, log=INFO)
        new_exception.resolve()
        self.logger.info.assert_called_with(f"An exception occurred during bot operation: {error_message}")

    def test_resolve_given_logging_level_warning_then_warning_logged(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger, log=WARNING)
        new_exception.resolve()
        self.logger.warning.assert_called_with(f"An exception occurred during bot operation: {error_message}")

    def test_resolve_given_logging_level_error_then_error_logged(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger, log=ERROR)
        new_exception.resolve()
        self.logger.error.assert_called_with(f"An exception occurred during bot operation: {error_message}")

    def test_resolve_given_logging_level_critical_then_critical_logged(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger, log=CRITICAL)
        new_exception.resolve()
        self.logger.critical.assert_called_with(f"An exception occurred during bot operation: {error_message}")

    def test_resolve_given_logging_not_specified_then_warning_logged(self):
        error_message = "Test error to be logged"
        new_exception = BotLoggedNoContextException(error_message, self.logger)
        new_exception.resolve()
        self.logger.warning.assert_called_with(f"An exception occurred during bot operation: {error_message}")
