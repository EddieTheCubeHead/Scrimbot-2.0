__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Converters.Convertable import Convertable
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestConvertable(AsyncUnittestBase):

    def setUp(self) -> None:
        self.convertable = Convertable()

    def test_set_converter_given_valid_provider_then_provider_set(self):
        mock_converter = MagicMock()
        Convertable.set_converter(mock_converter)
        self.assertEqual(self.convertable.converter, mock_converter)

    async def test_convert_given_string_then_provider_provide_called(self):
        mock_converter = AsyncMock()
        test_string = "Test"
        Convertable.converter = mock_converter
        mock_context = MagicMock()
        await self.convertable.convert(mock_context, test_string)
        mock_converter.convert.assert_called_with(mock_context, test_string)
        mock_converter.convert.assert_awaited()
