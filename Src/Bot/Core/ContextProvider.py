__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Message
from discord.ext.commands import Bot
from hintedi import HinteDI

from Src.Bot.Core.ScrimContext import ScrimContext


@HinteDI.singleton
class ContextProvider:
    """An abstraction layer between the bot and discord.py mainly used for overriding context creation in testing."""

    def __init__(self, context_class: type = ScrimContext):
        self.context_class = context_class

    async def get_context(self, client_super: Bot, message: Message):
        return await client_super.get_context(message, cls=self.context_class)
