from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

import inflect
from discord.ext.commands import Context
from sqlalchemy.orm import declared_attr, declarative_base

if TYPE_CHECKING:  # pragma: no cover
    from Bot.Converters.ConverterBase import ConverterBase


class _DataClass:

    @declared_attr
    def __tablename__(self):
        return inflect.engine().plural(self.__name__)  # pylint: disable=no-member

    converter = None


DataClass = declarative_base(cls=_DataClass)
