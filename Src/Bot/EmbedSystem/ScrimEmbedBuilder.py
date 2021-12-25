__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context
from discord.utils import remove_markdown

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Team import Team
from Bot.EmbedSystem.Helpers.UserNicknameService import UserNicknameService
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder
from Bot.Logic.ScrimManager import ScrimManager
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.DataClasses.ScrimState import ScrimState


def _build_team_participants(team: Team):
    if team.members:
        return "\n".join([f"<#{member.user_id}>" for member in team.members])
    return "_empty_"


@BotDependencyInjector.singleton
class ScrimEmbedBuilder(ResponseBuilder[ScrimManager]):

    DIVIDER_STRING = "----------------------------------------------"

    @BotDependencyInjector.inject
    def __init__(self, nickname_service: UserNicknameService):
        self._nickname_service = nickname_service

    def build(self, ctx: Context, displayable: ScrimManager) -> Embed:
        game = displayable.teams_manager.game
        min_players = game.team_count * game.min_team_size
        required_players = min_players - len(displayable.teams_manager.get_standard_teams()[0].members)
        embed = Embed(title="Status", description=f"Looking for players, {required_players} more required.",
                      color=game.colour)
        self._build_fields(embed, displayable)
        embed.set_author(name=f"{game.name} scrim", icon_url=game.icon)
        embed.set_footer(text="To join players react \U0001F3AE To join spectators react \U0001F441")
        return embed

    def _build_fields(self, embed: Embed, displayable: ScrimManager):
        embed.clear_fields()
        for team in displayable.teams_manager.get_standard_teams():
            if team.name == ScrimTeamsManager.QUEUE and not team.members:
                continue
            embed.add_field(name=team.name, value=_build_team_participants(team), inline=True)
        if displayable.state is not ScrimState.LFP:
            embed.add_field(name=self.DIVIDER_STRING, value=self.DIVIDER_STRING)
            for team in displayable.teams_manager.get_game_teams():
                embed.add_field(name=team.name, value=_build_team_participants(team))
