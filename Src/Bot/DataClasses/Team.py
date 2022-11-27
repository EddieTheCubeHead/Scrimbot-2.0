__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Optional

import discord
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.TeamMember import TeamMember
from Bot.DataClasses.User import User
from Bot.DataClasses.VoiceChannel import VoiceChannel


PARTICIPANTS = "Participants"
SPECTATORS = "Spectators"
QUEUE = "Queue"


class Team(DataClass):  # pragma: no-cover

    team_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # TODO: when teams are more refined, create check for these two
    code = Column(String, nullable=True)   # columns should be unique per guild with global guild (id=0) considered
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), nullable=False)

    # TODO: implement check for not allowing channels on global teams
    channel_id = Column(Integer, ForeignKey("VoiceChannels.channel_id"), nullable=True)

    guild = relationship("Guild", back_populates="teams")
    members = relationship("User", secondary=TeamMember.__table__, back_populates="teams")
    scrims = relationship("ParticipantTeam", back_populates="team")
    voice_channel = relationship("VoiceChannel", back_populates="teams", lazy="joined")

    def __init__(self, name: str, players: List[User] = None, min_size=0, max_size=0):
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
        self.members: List[User] = players if players is not None else []
        self.min_size: int = min_size
        self.max_size: int = max_size or min_size
        self.guild_id = 0
        self.is_pickup: bool = False
        self.winner: bool = False
        self.inline: bool = True
