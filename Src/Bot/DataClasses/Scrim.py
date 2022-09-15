from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
if TYPE_CHECKING:
    from Bot.Logic.ScrimManager import ScrimManager


class ScrimState(enum.Enum):
    LFP = 0,
    LOCKED = 1,
    STARTED = 2,
    ENDED = 3,
    CAPS = 4,
    VOICE_WAIT = 5,
    CAPS_PREP = 6,
    TERMINATED = 7


class Scrim(DataClass):  # pragma: no cover

    def __init__(self, scrim_manager: ScrimManager, state: ScrimState = ScrimState.LFP):
        self.channel_id = scrim_manager.message.channel.id
        self.game_name = scrim_manager.teams_manager.game.name
        self.game = scrim_manager.teams_manager.game
        self.state = state
        self.teams = []

    scrim_id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)
    state = Column(Enum(ScrimState), default=ScrimState.LFP)

    game = relationship("Game", back_populates="scrims")
    scrim_channel = relationship("ScrimChannel", back_populates="scrims")
    teams = relationship("ParticipantTeam", back_populates="scrim")
    results = relationship("UserScrimResult", back_populates="scrim")
