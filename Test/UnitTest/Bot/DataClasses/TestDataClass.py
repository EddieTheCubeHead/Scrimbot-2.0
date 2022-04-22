__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

import inflect

from Bot.DataClasses.DataClass import DataClass
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestDataClass(AsyncUnittestBase):

    def setUp(self) -> None:
        self.data_class = DataClass

    def test_init_tablename_is_plural_of_class_name(self):
        self.assertEqual(inflect.engine().plural(DataClass.__name__), self.data_class.__tablename__)
