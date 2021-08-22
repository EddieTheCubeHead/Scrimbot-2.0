__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC

from Bot.Converters.ConverterBase import ConverterBase


class Convertable(ABC):

    converter: ConverterBase = None

    @classmethod
    def set_converter(cls, converter: ConverterBase):
        cls.converter = converter
        return converter

    @classmethod
    async def convert(cls, argument: str):
        return await cls.converter.convert(argument)
