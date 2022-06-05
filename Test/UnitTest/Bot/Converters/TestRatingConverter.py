__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.RatingConverter import RatingConverter
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestRatingConverter(AsyncUnittestBase):

    def setUp(self) -> None:
        self.converter = RatingConverter()
        self.context = MagicMock()

    async def test_convert_when_called_with_valid_number_then_integer_returned(self):
        rating = 2222
        actual = await self.converter.convert(self.context, str(rating))
        self.assertEqual(rating, actual)

    async def test_convert_when_called_with_non_integer_argument_then_exception_raised(self):
        invalid_argument = "1124s"
        expected_exception = BotConversionFailureException("user rating", invalid_argument, reason="argument is not a "
                                                                                                   "whole number")
        await self._async_assert_raises_correct_exception(expected_exception, self.converter.convert, self.context,
                                                          invalid_argument)

    async def test_convert_when_called_with_negative_number_then_exception_raised(self):
        invalid_argument = "-11"
        expected_exception = BotConversionFailureException("user rating", invalid_argument, reason="rating is not "
                                                                                                   "between 0 and 5000")
        await self._async_assert_raises_correct_exception(expected_exception, self.converter.convert, self.context,
                                                          invalid_argument)
