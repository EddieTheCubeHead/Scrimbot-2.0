__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from Bot.Cogs.RatingCommands import RatingCommands
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestRatingCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.response_builder = AsyncMock()
        self.mock_user_rating_converter = MagicMock()
        self.mock_guild_converter = MagicMock()
        self.mock_embed_builder = AsyncMock()
        self.cog = RatingCommands(self.mock_user_rating_converter, self.mock_guild_converter, self.mock_embed_builder)
        self.cog._inject(MagicMock())

    async def test_rating_when_given_user_game_and_valid_rating_number_then_player_rating_set_and_stats_displayed(self):
        mock_user = MagicMock()
        mock_game = MagicMock()
        mock_context = MagicMock()
        rating = 1829
        mock_rating = MagicMock()
        mock_guild = MagicMock()
        self.mock_guild_converter.get_guild.return_value = mock_guild
        self.mock_user_rating_converter.create_user_rating.return_value = mock_rating
        await self.cog.rating(mock_context, mock_user, mock_game, rating)
        self.mock_guild_converter.get_guild.assert_called_with(mock_context.guild.id)
        self.mock_user_rating_converter.create_user_rating.assert_called_with(rating, mock_user, mock_game, mock_guild)
        self.mock_embed_builder.send.assert_called_with(mock_context, displayable=mock_rating)
