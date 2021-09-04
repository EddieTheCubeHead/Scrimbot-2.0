__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Dict, Union, Optional

import discord

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Team import Team
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


def _assert_valid_game(game):
    if game.team_count < 1:
        raise BotBaseInternalException("Tried to initialize a teams manager for a game with less than 1 teams.")
    if game.max_team_size and game.min_team_size > game.max_team_size:
        raise BotBaseInternalException("Tried to initialize a teams manager for a game with smaller team max size than"
                                       " team min size.")


def _is_full(team):
    return len(team.players) >= team.max_size


def _assert_valid_removal(player, team):
    if player not in team.players:
        raise BotBaseInternalException(f"Tried removing user '{player.display_name}' from team '{team.name}' "
                                       "even though they are not a member of the team.")


def is_in_guild_voice_chat(guild: discord.Guild, player: discord.Member):
    return player.voice is not None and player.voice.channel.guild.id == guild.id


def has_all_players_in_guild_voice_chat(team: Team):
    return all([is_in_guild_voice_chat(team.voice_channel.guild, player) for player in team.players])


async def _move_team_to_voice(team):
    for player in team.players:
        if player.voice:
            await player.move_to(team.voice_channel, reason="Setting up a scrim.")


class ScrimTeamsManager:
    """A class to be used inside a Scrim instance, meant for managing the separate teams in the scrim
    """
    PARTICIPANTS = "Participants"
    SPECTATORS = "Spectators"
    QUEUE = "Queue"

    def __init__(self, game: Game, team_channels: List[discord.VoiceChannel] = None, lobby: discord.VoiceChannel = None,
                 *, teams: List[Team] = None):
        _assert_valid_game(game)
        self._game: Game = game
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
        return len(self._teams[self.PARTICIPANTS].players) >= self._teams[self.PARTICIPANTS].min_size

    @property
    def has_full_teams(self):
        for team in self.get_game_teams():
            if not len(team.players) >= team.min_size:
                return False
        return True

    @property
    def has_participants(self):
        return len(self._teams[self.PARTICIPANTS].players) > 0

    @property
    def all_players_in_voice_chat(self):
        return all([has_all_players_in_guild_voice_chat(team) for team in self.get_game_teams()])

    def get_standard_teams(self):
        return list(self._teams.values())[self._game.team_count:]

    def get_game_teams(self):
        return list(self._teams.values())[:self._game.team_count]

    def _build_teams(self, premade_teams):

        teams = []
        for i in range(self._game.team_count):
            if len(premade_teams) > i:
                self._add_premade_team(premade_teams[i])
            else:
                self._add_new_team(i+1)
        return teams

    def _build_standard_teams(self):
        self._teams[self.PARTICIPANTS] = Team(self.PARTICIPANTS, [],
                                              self._game.min_team_size * self._game.team_count,
                                              self._game.max_team_size * self._game.team_count)
        self._teams[self.SPECTATORS] = Team(self.SPECTATORS)
        self._teams[self.QUEUE] = Team(self.QUEUE)

    def _add_new_team(self, team_number: int):
        team_name = f"Team {team_number}"
        self._teams[team_name] = Team(team_name, [], self._game.min_team_size, self._game.max_team_size)

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
            raise BotBaseUserException("Cannot create a scrim with a premade team name conflicting with a name "
                                       f"reserved for standard teams ({team.name})")

    def _assert_unique_team_name(self, team):
        if team.name in self._teams:
            raise BotBaseUserException(f"Cannot create a scrim with premade teams having identical names ({team.name})")

    def _assert_valid_team_size(self, team):
        if team.min_size < self._game.min_team_size or team.max_size > self._game.max_team_size:
            raise BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible with the"
                                       f" chosen game ({team.name})")

    def _assert_valid_team_players(self, team):
        if len(team.players) > self._game.max_team_size:
            raise BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible with the "
                                       f"chosen game ({team.name})")

    def _build_captains(self):
        captains = []
        for _ in range(self._game.team_count):
            captains.append(None)
        return captains

    def _add_channels_to_teams(self, channels: Optional[List[int]]):
        if channels:
            for index, channel in enumerate(channels):
                self._add_game_team_voice_channel(channel, index)

    def _add_game_team_voice_channel(self, channel, index):
        if self._is_game_team_index(index):
            self._get_team(index).voice_channel = channel

    def _is_game_team_index(self, index):
        return index < self._game.team_count

    def _add_lobby_channel(self, lobby):
        if lobby:
            for team in [self.PARTICIPANTS, self.SPECTATORS, self.QUEUE]:
                self._get_team(team).voice_channel = lobby

    def add_player(self, team: Union[int, str], player: discord.member):
        self._add_to_team(self._get_team(team), player)

    def _get_team(self, team: Union[int, str]) -> Team:
        if type(team) == str:
            return self._teams[team]
        return list(self._teams.values())[team]

    def _add_to_team(self, team: Team, player: discord.member):
        if self._is_full_participant_team(team):
            self._add_to_team(self._teams[self.QUEUE], player)
            return
        if self._is_full_game_team(team):
            raise BotBaseInternalException(f"Tried adding a player into a full team ({team.name})")
        team.players.append(player)

    def _is_full_participant_team(self, team: Team):
        return team.name == self.PARTICIPANTS and _is_full(team)

    def _is_full_game_team(self, team):
        return not self.is_reserved_name(team.name) and _is_full(team)

    def remove_player(self, team: Union[int, str], player: discord.member):
        self._remove_from_team(self._get_team(team), player)

    def _remove_from_team(self, team: Team, player: discord.member):
        _assert_valid_removal(player, team)
        if self._fill_participants_from_queue(team):
            team.players.append(self._teams[self.QUEUE].players.pop(0))
        team.players.remove(player)

    def _fill_participants_from_queue(self, team):
        return self._is_full_participant_team(team) and len(self._teams[self.QUEUE].players) > 0

    def set_team(self, team: Union[int, str], player: discord.Member):
        if not self._blind_remove(player):
            raise BotBaseInternalException(f"Tried setting team for user '{player.display_name}' who is not part of "
                                           f"the scrim.")
        self.add_player(team, player)

    def _blind_remove(self, player) -> bool:
        for team in self._teams.values():
            if player in team.players:
                self._remove_from_team(team, player)
                return True
        return False

    def clear_queue(self):
        self._get_team(self.QUEUE).players.clear()

    async def try_move_to_voice(self) -> bool:
        if not self.all_players_in_voice_chat:
            return False
        await self._move_players_to_voice()
        return True

    async def _move_players_to_voice(self):
        for team in self.get_game_teams():
            await _move_team_to_voice(team)
