__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

import inflect

from Bot.DataClasses.DataClass import DataClass
from Utils.AsyncUnittestBase import AsyncUnittestBase


class TestDataClass(AsyncUnittestBase):

    def setUp(self) -> None:
        self.data_class = DataClass

    def test_init_tablename_is_plural_of_class_name(self):
        self.assertEqual(inflect.engine().plural(DataClass.__name__), self.data_class.__tablename__)

    def test_set_provider_given_valid_provider_then_provider_set(self):
        mock_converter = MagicMock
        DataClass.set_converter(mock_converter)
        self.assertEqual(self.data_class.converter, mock_converter)

    async def test_convert_given_string_then_provider_provide_called(self):
        mock_converter = MagicMock()
        test_string = "Test"
        self.data_class.converter = mock_converter
        await self.data_class.convert(test_string)
        mock_converter.convert.assert_called_with(test_string)
