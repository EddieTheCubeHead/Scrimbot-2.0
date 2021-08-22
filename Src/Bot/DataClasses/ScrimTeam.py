__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Optional

import discord

from Bot.Converters.Convertable import Convertable


class ScrimTeam(Convertable):

    def __init__(self, name: str, players: List[discord.Member] = None, min_size=0, max_size=0):
        """The constructor of ScrimTeam

        :param name: The name of the team
        :type name: str
        :param players: The players of the team, default None,
        :type players: List[discord.Member]
        :param min_size: The minimum size of the team for it to be considered full, default 0 (no limit)
        :type min_size: int
        :param max_size: The maximum size of the team, default 0 (no limit)
        """

        self.name = name
        self.players: List[discord.Member] = players if players is not None else []
        self.min_size: int = min_size
        self.max_size: int = max_size or min_size
        self.voice_channel: Optional[discord.VoiceChannel] = None
        self.is_pickup: bool = False
        self.winner: bool = False
        self.inline: bool = True
