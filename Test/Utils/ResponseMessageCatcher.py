__version__ = "0.1"
__author__ = "Eetu Asikainen"

import queue

from discord import Message
from discord.ext.commands import Bot

from Bot.Core.ContextProvider import ContextProvider
from Utils.ResponseLoggerContext import ResponseLoggerContext


class ResponseMessageCatcher(ContextProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sent_queue = queue.Queue()

    async def get_context(self, client_super: Bot, message: Message):
        return await client_super.get_context(message, cls=ResponseLoggerContext)
