from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.DataClasses.Convertable import Convertable
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.VoiceChannel import VoiceChannel


class ScrimChannel(Convertable):

    channel_id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), nullable=False)

    guild = relationship("Guild", back_populates="scrim_channels")
    voice_channels = relationship("VoiceChannel", back_populates="parent_channel")
    scrims = relationship("Scrim", back_populates="scrim_channel")

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

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: ScrimChannelConverter):
        super().set_converter(converter)
