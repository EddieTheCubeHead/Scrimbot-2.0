__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Converter

from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException


class RatingConverter(Converter):

    async def convert(self, ctx, argument: str) -> int:
        try:
            rating = int(argument)
        except ValueError:
            raise BotConversionFailureException("user rating", argument, reason="argument is not a whole number")
        if rating < 0 or rating > 5000:
            raise BotConversionFailureException("user rating", argument, reason="rating is not between 0 and 5000")
        return rating
