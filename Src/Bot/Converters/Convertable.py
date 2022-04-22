__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Context, Converter

from Bot.Core.BotDependencyInjector import BotDependencyInjector


class Convertable:

    converter: Converter = None

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: Converter):
        cls.converter = converter
        return converter

    @classmethod
    async def convert(cls, ctx: Context, argument: str):
        if not cls.converter:
            cls.set_converter()
        return await cls.converter.convert(ctx, argument)
