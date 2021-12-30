__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Checks.ActiveScrimCheck import ActiveScrimCheck
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestFreeScrimCheck(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.check = ActiveScrimCheck()
        self.context = AsyncMock()
        self.mock_converter = MagicMock()
