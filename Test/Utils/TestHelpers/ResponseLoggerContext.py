from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import queue
from collections import OrderedDict
from datetime import datetime
from typing import Optional, Union
from unittest.mock import MagicMock, AsyncMock

from discord import Message, Reaction, Member
from discord.ext.commands import CommandError

from Bot.Core.ScrimContext import ScrimContext
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class MockReaction:

    def __init__(self, emoji: str, message: LoggedMessage, user: Optional[Member] = None):
        self._message = message
        self.emoji = emoji
        self.user = user

    def users(self):
        return [self.user] if self.user else []

    async def remove(self, member: Member):
        if member and self.user and member.id != self.user.id:
            raise CommandError("Silent erroneous reaction removal")
        await self._message.remove_reaction(self, member)


class LoggedMessage(Message):

    def __init__(self, *args, **kwargs):
        self._deletion_time: Optional[float] = None
        super().__init__(*args, **kwargs)
        self.reactions = []

    @property
    def deletion_time(self):
        return self._deletion_time

    @deletion_time.setter
    def deletion_time(self, time: float):
        self._deletion_time = time

    @property
    def raw_reactions(self):
        return [reaction.emoji for reaction in self.reactions]

    async def add_reaction(self, emoji, user=None):
        self.reactions.append(MockReaction(emoji, self, user))

    async def remove_reaction(self, emoji, member):
        for reaction in self.reactions:
            if (type(emoji) == str and reaction.emoji == emoji) or \
                    (type(emoji) != str and reaction.emoji == emoji.emoji):
                if (not member or type(emoji) == str) or (emoji.user and member.id == emoji.user.id):
                    self.reactions.remove(reaction)
                    return

    async def clear_reactions(self):
        self.reactions.clear()

    async def edit(self, **fields):
        self.content = fields.pop("content", self.content)
        self.embeds = [fields.pop("embed", self.embeds.pop(0) or [])]
        ResponseLoggerContext.add_sent(self.id, self, force_newest=True)


class ResponseLoggerContext(ScrimContext):
    sent_dict = OrderedDict()
    dict_index = 0
    id_mocker = TestIdGenerator()

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None,
                   allowed_mentions=None, reference=None, mention_author=None):
        message = LoggedMessage(state=AsyncMock(),
                                channel=self.channel,
                                data={"content": content, "embeds": [embed.to_dict()],
                                      "id": str(self.id_mocker.generate_viable_id()),
                                      "webhook_id": str(self.id_mocker.generate_viable_id()),
                                      "edited_timestamp": str(datetime.now()),
                                      "pinned": False,
                                      "tts": tts,
                                      "attachments": [],
                                      "type": "default",
                                      "mention_everyone": False})
        if delete_after is not None:
            message.deletion_time = delete_after
        self.add_sent(message.id, message)
        return message

    @classmethod
    def add_sent(cls, message_id: int, message: Message, *, force_newest=False):
        if force_newest:
            cls.sent_dict.pop(message_id)
        cls.sent_dict[message_id] = message

    @classmethod
    def get_oldest(cls) -> Message:
        if cls.dict_index >= len(cls.sent_dict):
            raise AssertionError("Tried getting a sent message while none exist!")
        message = list(cls.sent_dict.items())[cls.dict_index][1]
        cls.dict_index += 1
        return message

    @classmethod
    def reset_position(cls):
        cls.dict_index = len(cls.sent_dict.items())

    @classmethod
    def full_reset(cls):
        cls.sent_dict = OrderedDict()
        cls.dict_index = 0
