__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

import discord

from Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimTeam import ScrimTeam


class TeamManager:
    """A class to be used inside a Scrim instance, meant for managing the separate teams in the scrim
    """

    def __init__(self, game: Game, team_1_channel=None, team_2_channel=None, *, team_1: ScrimTeam = None,
                 team_2: ScrimTeam = None):
        self._participants: ScrimTeam = ScrimTeam.from_scrim_data(game.playercount, "Participants", None)
        self._queue: ScrimTeam = ScrimTeam.from_scrim_data(game.playercount, "Queue", None)
        self._spectators: ScrimTeam = ScrimTeam.from_scrim_data(game.playercount, "Spectators", None)
        if team_1 is None:
            self._team_1: ScrimTeam = ScrimTeam.from_scrim_data(game.playercount, "Team 1", team_1_channel)
        else:
            self._team_1: ScrimTeam = team_1
            self._team_1.set_voice_channel(team_1_channel)

        if team_2 is None:
            self._team_2: ScrimTeam = ScrimTeam.from_scrim_data(game.playercount, "Team 2", team_2_channel)
        else:
            self._team_2: ScrimTeam = team_2
            self._team_2.set_voice_channel(team_2_channel)

        self._cap_1: Optional[discord.Member] = None
        self._cap_2: Optional[discord.Member] = None


