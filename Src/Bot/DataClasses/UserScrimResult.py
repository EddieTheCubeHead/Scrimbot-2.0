__version__ = "0.1"
__author__ = "Eetu Asikainen"

import enum

from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass


class Result(enum.Enum):
    UNREGISTERED = 0
    WIN = 1
    LOSS = 2
    TIE = 3


class UserScrimResult(DataClass):  # pragma: no cover
    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    scrim_id = Column(Integer, ForeignKey("Scrims.scrim_id"), primary_key=True)
    rating_id = Column(Integer, ForeignKey("UserRatings.rating_id"), default=None)
    frozen_rating = Column(Integer, nullable=False)
    result = Column(Enum(Result), default=Result.UNREGISTERED)

    rating = relationship("UserRating", back_populates="results")
    scrim = relationship("Scrim", back_populates="results")

    def __init__(self, rating_id: int, user_id: int, scrim_id: int, frozen_rating: int,
                 result: Result = Result.UNREGISTERED):
        self.rating_id = rating_id
        self.user_id = user_id
        self.scrim_id = scrim_id
        self.frozen_rating = frozen_rating
        self.result = result
