__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

import inflect

from Bot.DataClasses.Convertable import Convertable
from Utils.AsyncUnittestBase import AsyncUnittestBase


class TestConvertable(AsyncUnittestBase):

    def setUp(self) -> None:
        self.convertable = Convertable

    def test_init_tablename_is_plural_of_class_name(self):
        self.assertEqual(inflect.engine().plural(Convertable.__name__), self.convertable.__tablename__)

    def test_set_provider_given_valid_provider_then_provider_set(self):
        mock_converter = MagicMock
        Convertable.set_converter(mock_converter)
        self.assertEqual(self.convertable.converter, mock_converter)

    async def test_convert_given_string_then_provider_provide_called(self):
        mock_converter = AsyncMock()
        test_string = "Test"
        self.convertable.converter = mock_converter
        await self.convertable.convert(test_string)
        mock_converter.convert.assert_called_with(test_string)
