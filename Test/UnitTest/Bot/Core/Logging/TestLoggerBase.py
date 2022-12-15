__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
from unittest.mock import MagicMock

import UnitTest
from Src.Bot.Core.Logging.LoggerBase import LoggerBase
from Test.Utils.TestBases.UnittestBase import UnittestBase


class TestLoggerBase(UnittestBase):
    file_folder: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.file_folder = f"{os.path.dirname(UnitTest.Bot.Core.Logging.__file__)}\\LoggerBaseTest"
        os.mkdir(cls.file_folder)

    def setUp(self) -> None:
        config = MagicMock()
        config.file_folder = self.file_folder
        self.logger = LoggerBase("TestLogger", config)

    def test_init_when_called_with_name_and_config_then_name_and_file_folder_set(self):
        self.assertEqual("TestLogger", self.logger.name)
        handler = self.logger.handlers.pop(0)
        handler_repr = str(handler)
        handler.close()
        self.assertEqual(f"<FileHandler {self.file_folder}\\scrim_bot.log (NOTSET)>", handler_repr)

    def test_init_when_called_then_formatting_set_correctly(self):
        self.assertEqual("TestLogger", self.logger.name)
        handler = self.logger.handlers.pop(0)
        formatter_style = handler.formatter.__getattribute__("_fmt")
        handler.close()
        self.assertEqual('%(name)-36s || %(asctime)s || %(levelname)-8s || %(message)s', formatter_style)

    def tearDown(self) -> None:
        for handler in self.logger.handlers:
            handler.close()
        os.remove(f"{self.file_folder}/scrim_bot.log")

    @classmethod
    def tearDownClass(cls) -> None:
        os.rmdir(cls.file_folder)
