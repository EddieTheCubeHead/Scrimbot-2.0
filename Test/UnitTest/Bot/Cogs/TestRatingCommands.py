__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from Bot.Cogs.RatingCommands import RatingCommands
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestRatingCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.response_builder = AsyncMock()
        self.mock_user_rating_converter = MagicMock()
        self.cog = RatingCommands(self.mock_user_rating_converter)
        self.cog._inject(MagicMock())

    async def test_rating_when_given_user_game_and_valid_rating_number_then_player_rating_set_and_stats_displayed(self):
        mock_user = MagicMock()
        mock_game = MagicMock()
        mock_context = MagicMock()
        rating = 1829
        await self.cog.rating(mock_context, mock_user, mock_game, rating)
        self.mock_user_rating_converter.set_user_rating.assert_called_with(rating, mock_user, mock_game,
                                                                           mock_context.guild)
