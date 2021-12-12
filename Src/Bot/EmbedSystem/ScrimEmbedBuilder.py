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


@BotDependencyInjector.singleton
class ScrimEmbedBuilder(ResponseBuilder[ScrimManager]):

    DIVIDER_STRING = "----------------------------------------------"

    @BotDependencyInjector.inject
    def __init__(self, nickname_service: UserNicknameService):
        self._nickname_service = nickname_service

    def build(self, ctx: Context, displayable: ScrimManager) -> Embed:
        game = displayable.teams_manager.game
        min_players = game.team_count * game.min_team_size
        embed = Embed(title="Status", description=f"Looking for players, {min_players} more required.",
                      color=game.colour)
        self._build_fields(ctx, embed, displayable)
        embed.set_author(name=f"{game.name} scrim", icon_url=game.icon)
        embed.set_footer(text="To join players react \U0001F3AE To join spectators react \U0001F441")
        return embed

    def _build_fields(self, ctx: Context, embed: Embed, displayable: ScrimManager):
        embed.clear_fields()
        for team in displayable.teams_manager.get_standard_teams():
            if team.name == ScrimTeamsManager.QUEUE and not team.members:
                continue
            embed.add_field(name=team.name, value=self._build_team_participants(ctx, team), inline=True)
        game_teams = displayable.teams_manager.get_game_teams()
        if game_teams and displayable.state is not ScrimState.LFP:
            embed.add_field(name=self.DIVIDER_STRING, value=self.DIVIDER_STRING)
            for team in game_teams:
                embed.add_field(name=team.name, value=self._build_team_participants(ctx, team))

    def _build_team_participants(self, ctx: Context, team: Team):
        if team.members:
            member_names = [self._nickname_service.get_name(ctx, player.user_id) for player in team.members]
            cleaned_names = [remove_markdown(name) for name in member_names]
            return "\n".join(cleaned_names)
        return "__empty__"
