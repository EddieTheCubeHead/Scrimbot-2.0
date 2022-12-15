__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.DataClasses.UserScrimResult import Result
from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.UserRating import UserRating
from Src.Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


@HinteDI.instance
class RatingEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, rating: UserRating) -> Embed:
        embed = Embed(title="Player statistics", description=f"<@!{rating.user_id}>", colour=rating.game.colour)
        embed.set_author(name=rating.game_name, icon_url=rating.game.icon)
        embed.set_thumbnail(url=rating.user.member.avatar_url)
        self._build_fields(embed, rating)
        return embed

    @staticmethod
    def _build_fields(embed: Embed, rating: UserRating):
        games = len(rating.results)
        wins = len(list(filter(lambda x: x.result == Result.WIN, rating.results)))
        ties = len(list(filter(lambda x: x.result == Result.TIE, rating.results)))
        unrecorded = len(list(filter(lambda x: x.result == Result.UNREGISTERED, rating.results)))
        losses = games - wins - ties - unrecorded
        embed.add_field(name="Games played", value=str(games))
        embed.add_field(name="Wins", value=str(wins))
        embed.add_field(name="Losses", value=str(losses))
        embed.add_field(name="Ties", value=str(ties))
        embed.add_field(name="Unrecorded", value=str(unrecorded))
        embed.add_field(name="Rating", value=str(rating.rating))
