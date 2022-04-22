__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Converter

from Bot.Core.BotDependencyInjector import BotDependencyInjector


@BotDependencyInjector.singleton
class TeamCreationStrategyConverter(Converter):

    _strategies: dict[str, Converter] = {}

    async def convert(self, ctx, argument):
        if argument in self._strategies:
            return self._strategies[argument]

    @classmethod
    def register(cls, name: str):
        def wrapper(converter_class):
            cls._strategies[name] = converter_class()
            return converter_class
        return wrapper
