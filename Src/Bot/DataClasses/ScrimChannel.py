from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.DataClasses.VoiceChannel import VoiceChannel


@BotDependencyConstructor.convertable
class ScrimChannel(Convertable):

    channel_id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), nullable=False)

    guild = relationship("Guild", back_populates="scrim_channels")
    voice_channels = relationship("VoiceChannel", back_populates="parent_channel")

    def __init__(self, channel_id: int, guild_id: int, *voice_channels: VoiceChannel):
        """A constructor for the Scrim class

        args
        ----

        :param channel_id: The text channel the scrim is registered to
        :type channel_id: discord.TextChannel
        :param guild_id: The server id of the server the scrim belongs to
        :type guild_id: int
        :param voice_channels: The voice channels that are associated with the scrim
        :type voice_channels: list[int]
        """

        self.channel_id: int = channel_id
        self.guild_id: int = guild_id
        self.voice_channels: list[VoiceChannel] = list(voice_channels)
