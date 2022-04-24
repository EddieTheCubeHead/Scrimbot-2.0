from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass


class Prefix(DataClass):  # pragma: no cover

    prefix = Column(String, primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), primary_key=True)

    guild = relationship("Guild", back_populates="prefixes")
