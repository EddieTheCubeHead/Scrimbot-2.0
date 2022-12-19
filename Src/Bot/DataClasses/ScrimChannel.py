from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from hintedi import HinteDI

from Src.Bot.Converters.Convertable import Convertable
from Src.Bot.DataClasses.Displayable import Displayable

if TYPE_CHECKING:  # pragma: no cover
    from Src.Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Src.Bot.DataClasses.DataClass import DataClass
from Src.Bot.DataClasses.VoiceChannel import VoiceChannel


class ScrimChannel(DataClass, Convertable):  # pragma: no cover

    channel_id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), nullable=False)

    guild = relationship("Guild", back_populates="scrim_channels")
    voice_channels = relationship("VoiceChannel", back_populates="parent_channel")
    scrims = relationship("Scrim", back_populates="scrim_channel")

    def __init__(self, channel_id: int, guild_id: int, *voice_channels: VoiceChannel):
        super().__init__()
        self.channel_id: int = channel_id
        self.guild_id: int = guild_id
        self.voice_channels: list[VoiceChannel] = list(voice_channels)

    @classmethod
    @HinteDI.inject
    def set_converter(cls, converter: ScrimChannelConverter):  # pragma: no cover
        super().set_converter(converter)
