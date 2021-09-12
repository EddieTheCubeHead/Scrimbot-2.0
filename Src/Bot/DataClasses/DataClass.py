from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

import inflect
from sqlalchemy.orm import declared_attr, declarative_base

if TYPE_CHECKING:  # pragma no-cover
    from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector


class _DataClass:

    @declared_attr
    def __tablename__(self):
        return inflect.engine().plural(self.__name__)  # pylint: disable=no-member

    converter = None

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: ConverterBase):
        cls.converter = converter
        return converter

    @classmethod
    async def convert(cls, argument: str) -> _DataClass:
        if not cls.converter:
            cls.set_converter()
        return cls.converter.convert(argument)


DataClass = declarative_base(cls=_DataClass)
