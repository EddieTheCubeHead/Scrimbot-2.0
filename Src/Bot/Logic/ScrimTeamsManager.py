__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Dict, Union, Optional

import discord

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Game import Game
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Bot.Exceptions.BotLoggedContextException import BotLoggedContextException
from Bot.Exceptions.BotInvalidPlayerRemoval import BotInvalidPlayerRemoval
from Bot.Logic.ScrimParticipantManager import ScrimParticipantManager


def _assert_valid_game(game):
    if game.team_count < 1:
        raise BotLoggedContextException("Tried to initialize a teams manager for a game with less than 1 teams.")
    if game.max_team_size and game.min_team_size > game.max_team_size:
        raise BotLoggedContextException("Tried to initialize a teams manager for a game with smaller team max size "
                                        "than team min size.")


def _is_full(team):
    return len(team.members) >= team.max_size


def is_in_guild_voice_chat(scrim_channel: ScrimChannel, player: discord.Member):
    return player.voice is not None and scrim_channel and player.voice.channel.guild.id == scrim_channel.guild_id


def _assert_valid_removal(player, team):
    if player.user_id not in [member.user_id for member in team.members]:
        raise BotInvalidPlayerRemoval(player, team)


class ScrimTeamsManager:
    """A class to be used inside a Scrim instance, meant for managing the separate teams in the scrim"""

    PARTICIPANTS = "Participants"
    SPECTATORS = "Spectators"
    QUEUE = "Queue"

    # TODO extract data into separate DTO
    @BotDependencyInjector.inject
    def __init__(self, game: Game, participant_manager: ScrimParticipantManager, *,
                 team_channels: List[discord.VoiceChannel] = None, lobby: discord.VoiceChannel = None,
                 teams: List[Team] = None):
        _assert_valid_game(game)
        self.game: Game = game
        self._participant_manager: ScrimParticipantManager = participant_manager
        self._teams: Dict[str, Team] = {}
        self._build_teams(teams or [])
        self._build_standard_teams()
        self._captains = self._build_captains()
        self._add_channels_to_teams(team_channels)
        self._add_lobby_channel(lobby)

    @classmethod
    def is_reserved_name(cls, team_name: str):
        return team_name in [cls.PARTICIPANTS, cls.SPECTATORS, cls.QUEUE]

    @property
    def has_enough_participants(self):
        return len(self._teams[self.PARTICIPANTS].members) >= self._teams[self.PARTICIPANTS].min_size

    @property
    def has_full_teams(self):
        for team in self.get_game_teams():
            if not len(team.members) >= team.min_size:
                return False
        return True

    @property
    def has_participants(self):
        return len(self._teams[self.PARTICIPANTS].members) > 0

    @property
    def all_players_in_voice_chat(self):
        return all(self.has_all_players_in_guild_voice_chat(team) for team in self.get_game_teams())

    def has_all_players_in_guild_voice_chat(self, team: Team):
        if not team.voice_channel:
            return False
        participant_members = [self._participant_manager.try_get_participant(player.user_id) for player in team.members]
        return all(is_in_guild_voice_chat(team.voice_channel.parent_channel, member) for member in participant_members)

    def get_standard_teams(self):
        return list(self._teams.values())[self.game.team_count:]

    def get_game_teams(self):
        return list(self._teams.values())[:self.game.team_count]

    def _build_teams(self, premade_teams):

        teams = []
        for i in range(self.game.team_count):
            if len(premade_teams) > i:
                self._add_premade_team(premade_teams[i])
            else:
                self._add_new_team(i + 1)
        return teams

    def _build_standard_teams(self):
        self._teams[self.PARTICIPANTS] = Team(self.PARTICIPANTS, [],
                                              self.game.min_team_size * self.game.team_count,
                                              self.game.max_team_size * self.game.team_count)
        self._teams[self.SPECTATORS] = Team(self.SPECTATORS)
        self._teams[self.QUEUE] = Team(self.QUEUE)

    def _add_new_team(self, team_number: int):
        team_name = f"Team {team_number}"
        self._teams[team_name] = Team(team_name, [], self.game.min_team_size, self.game.max_team_size)

    def _add_premade_team(self, team: Team):
        self._assert_valid_team(team)
        self._teams[team.name] = team

    def _assert_valid_team(self, team):
        self._assert_not_standard_team_name(team)
        self._assert_unique_team_name(team)
        self._assert_valid_team_size(team)
        self._assert_valid_team_players(team)

    def _assert_not_standard_team_name(self, team):
        if self.is_reserved_name(team.name):
            raise BotBaseRespondToContextException(f"Cannot create a scrim with a premade team name conflicting with a "
                                                   f"name reserved for standard teams ({team.name})")

    def _assert_unique_team_name(self, team):
        if team.name in self._teams:
            raise BotBaseRespondToContextException(f"Cannot create a scrim with premade teams having identical names "
                                                   f"({team.name})")

    def _assert_valid_team_size(self, team):
        if team.min_size < self.game.min_team_size or team.max_size > self.game.max_team_size:
            raise BotBaseRespondToContextException(f"Cannot create a scrim with a premade team with a size incompatible"
                                                   f" with the chosen game ({team.name})")

    def _assert_valid_team_players(self, team):
        if len(team.members) > self.game.max_team_size:
            raise BotBaseRespondToContextException(f"Cannot create a scrim with a premade team with a size incompatible"
                                                   f" with the chosen game ({team.name})")

    def _build_captains(self):
        captains = []
        for _ in range(self.game.team_count):
            captains.append(None)
        return captains

    def _add_channels_to_teams(self, channels: Optional[List[int]]):
        if channels:
            for index, channel in enumerate(channels):
                self._add_game_team_voice_channel(channel, index)

    def _add_game_team_voice_channel(self, channel, index):
        if self._is_game_team_index(index):
            team = self._get_team(index)
            team.voice_channel = channel

    def _is_game_team_index(self, index):
        return index < self.game.team_count

    def _add_lobby_channel(self, lobby):
        if lobby:
            for team in [self.PARTICIPANTS, self.SPECTATORS, self.QUEUE]:
                self._get_team(team).voice_channel = lobby

    def add_player(self, team: Union[int, str], player: User):
        self._add_to_team(self._get_team(team), player)

    def _get_team(self, team: Union[int, str]) -> Team:
        if isinstance(team, str):
            return self._teams[team]
        return list(self._teams.values())[team]

    def _add_to_team(self, team: Team, player: User):
        if self._is_full_participant_team(team):
            self._add_to_team(self._teams[self.QUEUE], player)
            return
        if self._is_full_game_team(team):
            raise BotInvalidJoinException(player, team, "Could not add a player into a full team.")
        self._assert_teamless(team, player)
        team.members.append(player)

    def _assert_teamless(self, team: Team, player: User):
        player_team = self._try_get_team(player)
        if player_team:
            raise BotInvalidJoinException(player, team, f"already a member of the team '{player_team.name}'")

    def _is_full_participant_team(self, team: Team):
        return team.name == self.PARTICIPANTS and _is_full(team)

    def _is_full_game_team(self, team):
        return not self.is_reserved_name(team.name) and _is_full(team)

    def remove_player(self, team: Union[int, str], player: User):
        self._remove_from_team(self._get_team(team), player)

    def _remove_from_team(self, team: Team, player: User):
        _assert_valid_removal(player, team)
        if self._should_fill_participants_from_queue(team):
            team.members.append(self._teams[self.QUEUE].members.pop(0))
        for member in team.members:
            if member.user_id == player.user_id:
                team.members.remove(member)
                break

    def _should_fill_participants_from_queue(self, team: Team) -> bool:
        return self._is_full_participant_team(team) and len(self._teams[self.QUEUE].members) > 0

    def set_team(self, team: Union[int, str], player: User):
        if self._is_full_game_team(self._get_team(team)):
            raise BotInvalidJoinException(player, self._get_team(team), "Could not add a player into a full team.")
        if not self._blind_remove(player):
            raise BotInvalidPlayerRemoval(player, self._get_team(team))
        self.add_player(team, player)

    def _blind_remove(self, player: User) -> bool:
        for team in self._teams.values():
            if player.user_id in [member.user_id for member in team.members]:
                self._remove_from_team(team, player)
                return True
        return False

    def clear_queue(self):
        self._get_team(self.QUEUE).members.clear()

    async def try_move_to_voice(self) -> bool:
        if not self.all_players_in_voice_chat:
            return False
        await self._move_players_to_voice()
        return True

    async def _move_players_to_voice(self):
        for team in self.get_game_teams():
            await self._move_team_to_voice(team)

    async def _move_team_to_voice(self, team):
        for player in team.members:
            member = self._participant_manager.try_get_participant(player.user_id)
            if member.voice:
                await member.move_to(team.voice_channel, reason="Setting up a scrim.")

    def _try_get_team(self, player) -> Optional[Team]:
        for team in self._teams.values():
            if player.user_id in [member.user_id for member in team.members]:
                return team
