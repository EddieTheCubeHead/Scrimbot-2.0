__version__ = "0.1"
__author__ = "Eetu Asikainen"

import queue

from discord import Message
from discord.ext.commands import Bot

from Bot.Core.ContextProvider import ContextProvider
from Test.Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext


class ResponseMessageCatcher(ContextProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_guild_admin = False
        self.sent_queue = queue.Queue()

    def set_administrator_status(self, is_guild_admin: bool):
        self._is_guild_admin = is_guild_admin

    async def get_context(self, client_super: Bot, message: Message):
        context = await client_super.get_context(message, cls=ResponseLoggerContext)
        context.author.guild_permissions.administrator = self._is_guild_admin
        return context
