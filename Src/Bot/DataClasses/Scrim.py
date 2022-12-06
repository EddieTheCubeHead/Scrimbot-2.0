from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import enum
from typing import TYPE_CHECKING

from discord import Message
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass

if TYPE_CHECKING:
    from Bot.DataClasses.Game import Game
    from Bot.DataClasses.ScrimChannel import ScrimChannel
    from Bot.DataClasses.Team import Team
from Bot.DataClasses.ParticipantTeam import ParticipantTeam


class ScrimState(enum.Enum):
    SETTING_UP = 0,
    LFP = 1,
    LOCKED = 2,
    STARTED = 3,
    ENDED = 4,
    CAPS = 5,
    VOICE_WAIT = 6,
    CAPS_PREP = 7,
    TERMINATED = 8


class Scrim(DataClass):  # pragma: no cover

    def __init__(self, message: Message | None, game: Game, state: ScrimState = ScrimState.LFP):
        if message is not None:
            self.channel_id = message.channel.id
            self.message_id = message.id
        self.game_name = game.name
        self.game = game
        self.state = state
        self.teams: list[Team] = []

    scrim_id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)
    state = Column(Enum(ScrimState), default=ScrimState.LFP)
    message_id = Column(Integer, unique=True)
    terminator_id = Column(Integer, default=None)

    game = relationship("Game", back_populates="scrims")
    scrim_channel = relationship("ScrimChannel", back_populates="scrims")
    teams = relationship("ParticipantTeam", back_populates="scrim")
    results = relationship("UserScrimResult", back_populates="scrim")
