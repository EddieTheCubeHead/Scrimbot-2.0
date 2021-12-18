__version__ = "0.1"
__author__ = "Eetu Asikainen"

import queue
from collections import OrderedDict
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from discord import Message
from Bot.Core.ScrimContext import ScrimContext
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class LoggedMessage(Message):

    def __init__(self, *args, **kwargs):
        self.test_reactions = []
        super().__init__(*args, **kwargs)

    async def add_reaction(self, emoji):
        self.test_reactions.append(emoji)

    async def edit(self, **fields):
        ResponseLoggerContext.add_sent(self.id, self)


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
        self.add_sent(message.id, message)
        return message

    @classmethod
    def add_sent(cls, message_id: int, message: Message):
        cls.sent_dict[message_id] = message

    @classmethod
    def get_oldest(cls) -> Message:
        if cls.dict_index >= len(cls.sent_dict):
            raise AssertionError("Tried getting a sent message while none exist!")
        message = list(cls.sent_dict.items())[cls.dict_index][1]
        cls.dict_index += 1
        return message

    @classmethod
    def reset(cls):
        cls.dict_index = len(cls.sent_dict.items())
