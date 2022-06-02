__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.UserRating import UserRating
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


@BotDependencyInjector.instance
class RatingEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, rating: UserRating) -> Embed:
        embed = Embed(title="Player statistics", description=f"<@!{rating.user_id}>", colour=rating.game.colour)
        embed.set_author(name=rating.game_name, icon_url=rating.game.icon)
        embed.set_thumbnail(url=rating.user.member.display_avatar.url)
        self._build_fields(embed, rating)
        return embed

    @staticmethod
    def _build_fields(embed: Embed, rating: UserRating):
        results = [scrim for team in rating.user.teams for scrim in team.scrims]
        games = len(results)
        wins = len(list(filter(lambda x: x.placement == 1 and not x.tied, results)))
        ties = len(list(filter(lambda x: x.placement == 1 and x.tied, results)))
        unrecorded = len(list(filter(lambda x: x.placement == 0, results)))
        losses = games - wins - ties - unrecorded
        embed.add_field(name="Games played", value=str(games))
        embed.add_field(name="Wins", value=str(wins))
        embed.add_field(name="Losses", value=str(losses))
        embed.add_field(name="Ties", value=str(losses))
        embed.add_field(name="Unrecorded", value=str(unrecorded))
        embed.add_field(name="Rating", value=str(rating.rating))
