__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable


class Alias(Convertable):
    name = Column(String, primary_key=True)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)

    game = relationship("Game", back_populates="aliases")

