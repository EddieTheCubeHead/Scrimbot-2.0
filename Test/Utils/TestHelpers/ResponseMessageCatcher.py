__version__ = "0.1"
__author__ = "Eetu Asikainen"

import queue
from contextlib import contextmanager
from unittest.mock import AsyncMock

from discord import Message
from discord.ext.commands import Bot

from Src.Bot.Core.ContextProvider import ContextProvider
from Test.Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext


class ResponseMessageCatcher(ContextProvider):

    guild = AsyncMock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_guild_admin = False
        self.sent_queue = queue.Queue()

    def set_administrator_status(self, is_guild_admin: bool):
        self._is_guild_admin = is_guild_admin

    @contextmanager
    def as_admin(self):
        original_admin_status = self._is_guild_admin
        try:
            self._is_guild_admin = True
            yield
        finally:
            self._is_guild_admin = original_admin_status

    async def get_context(self, client_super: Bot, message: Message):
        context = await client_super.get_context(message, cls=ResponseLoggerContext)
        context.author.guild_permissions.administrator = self._is_guild_admin
        return context
