__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Type

from discord.ext import commands

from Bot.Exceptions.BotBaseUserException import BotBaseUserException


class BotConversionFailureException(BotBaseUserException, commands.ConversionError):

    def __init__(self, conversion_type: str, argument: str):
        self.conversion_type = conversion_type
        self.argument = argument

    def get_description(self) -> str:
        return f"Could not convert argument '{self.argument}' into type {self.conversion_type}"
