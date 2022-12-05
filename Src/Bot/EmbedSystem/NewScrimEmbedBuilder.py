__version__ = "0.1"
__author__ = "Eetu Asikainen"


from discord import Embed
from hintedi import HinteDI

from Bot.DataClasses.Scrim import Scrim
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


def _build_fields(embed: Embed, fields: list[(str, str, bool)]):
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)


@HinteDI.singleton
class NewScrimEmbedBuilder(ResponseBuilder[Scrim]):

    DIVIDER_STRING = "----------------------------------------------"

    @HinteDI.inject
    def __init__(self, state_provider: ScrimStateBase):
        self._state_provider = state_provider

    def build(self, ctx, scrim: Scrim) -> Embed:
        game = scrim.game
        scrim_state = self._state_provider.resolve_from_key(scrim.state)
        embed = Embed(title="Status", description=scrim_state.build_description(scrim),
                      color=game.colour)
        _build_fields(embed, scrim_state.build_fields(scrim))
        embed.set_author(name=f"{game.name} scrim", icon_url=game.icon)
        embed.set_footer(text=scrim_state.build_footer(scrim))
        return embed
