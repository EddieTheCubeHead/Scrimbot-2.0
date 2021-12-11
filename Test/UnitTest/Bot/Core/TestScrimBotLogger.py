__version__ = "ver"
__author__ = "Eetu Asikainen"

import os
import re
from logging import DEBUG, Formatter, FileHandler
from unittest.mock import MagicMock

import UnitTest
from Bot.Core.ScrimBotLogger import ScrimBotLogger
from Utils.TestBases.UnittestBase import UnittestBase


class TestScrimBotLogger(UnittestBase):

    file_folder: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.file_folder = f"{os.path.dirname(UnitTest.Bot.Core.__file__)}/logging_test_folder"
        os.mkdir(f"{cls.file_folder}")

    def setUp(self) -> None:
        config = MagicMock()
        config.file_folder = self.file_folder
        self.logger = ScrimBotLogger(config)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimBotLogger)

    def test_debug_when_called_then_logged_correctly(self):
        self.logger.debug("Test debug message")
        self._assert_logged([r"DEBUG \|\| Test debug message"])

    def test_warning_when_called_then_logged_correctly(self):
        self.logger.warning("Test warning message")
        self._assert_logged([r"WARNING \|\| Test warning message"])

    def test_error_when_called_then_logged_correctly(self):
        self.logger.error("Test error message")
        self._assert_logged([r"ERROR \|\| Test error message"])

    def test_critical_when_called_then_logged_correctly(self):
        self.logger.critical("Test critical message")
        self._assert_logged([r"CRITICAL \|\| Test critical message"])

    def tearDown(self) -> None:
        for handler in self.logger.handlers:
            handler.close()
        os.remove(f"{self.file_folder}/scrim_bot.log")

    @classmethod
    def tearDownClass(cls) -> None:
        os.rmdir(cls.file_folder)

    def _assert_logged(self, messages: list[str]):
        with open(f"{self.file_folder}/scrim_bot.log", encoding="utf-8", mode="r") as log_file:
            for expected, actual in zip(messages, log_file):
                regex = r"^[\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2},[\d]{3} \|\| " + expected + r"$"
                self.assertRegex(actual, regex)
