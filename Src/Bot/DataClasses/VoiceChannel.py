import discord
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable


class VoiceChannel(Convertable):

    channel_id = Column(Integer, primary_key=True)
    parent_channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    team = Column(Integer, nullable=False)

    parent_channel = relationship("ScrimChannel", back_populates="voice_channels")
    teams = relationship("ScrimTeam", back_populates="voice_channel")

    def __init__(self, channel_id: int, parent_channel_id: int, team: int):
        """A constructor for the Scrim class

        args
        ----

        :param channel_id: The text channel the scrim is registered to
        :type channel_id: discord.TextChannel
        :param parent_channel_id: The server id of the server the scrim belongs to
        :type parent_channel_id: int
        :param team: The voice channels that are associated with the scrim
        :type team: list[int]
        """

        self.channel_id: int = channel_id
        self.parent_channel_id: int = parent_channel_id
        self.team: int = team
