from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC


class Convertable(ABC):

    converter = None

    @classmethod
    def set_converter(cls, converter):
        cls.converter = converter
        return converter

    @classmethod
    async def convert(cls, argument: str) -> Convertable:
        return await cls.converter.convert(argument)
