from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import inflect
from sqlalchemy.orm import declared_attr, declarative_base


class _Convertable:

    @declared_attr
    def __tablename__(self):
        return inflect.engine().plural(self.__name__)  # pylint: disable=no-member

    converter = None

    @classmethod
    def set_converter(cls, converter):
        cls.converter = converter
        return converter

    @classmethod
    async def convert(cls, argument: str) -> _Convertable:
        return await cls.converter.convert(argument)


Convertable = declarative_base(cls=_Convertable)
