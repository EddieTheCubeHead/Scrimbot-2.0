__version__ = "0.1"
__author__ = "Eetu Asikainen"


from discord import Embed
from hintedi import HinteDI

from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder
from Bot.Logic.ScrimManager import ScrimManager


def _build_fields(embed: Embed, fields: list[(str, str, bool)]):
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)


@HinteDI.singleton
class ScrimEmbedBuilder(ResponseBuilder[ScrimManager]):

    DIVIDER_STRING = "----------------------------------------------"

    def build(self, ctx, scrim_manager: ScrimManager) -> Embed:
        game = scrim_manager.teams_manager.game
        embed = Embed(title="Status", description=scrim_manager.build_description(),
                      color=game.colour)
        _build_fields(embed, scrim_manager.build_fields())
        embed.set_author(name=f"{game.name} scrim", icon_url=game.icon)
        embed.set_footer(text=scrim_manager.build_footer())
        return embed
