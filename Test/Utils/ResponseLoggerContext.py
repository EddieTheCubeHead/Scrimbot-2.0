__version__ = "0.1"
__author__ = "Eetu Asikainen"

import queue

from discord import Embed
from Bot.Core.ScrimContext import ScrimContext


class ResponseLoggerContext(ScrimContext):
    sent_queue = queue.Queue()

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None,
                   allowed_mentions=None, reference=None, mention_author=None):
        self._add_sent(content, embed=embed, delete_after=delete_after)

    @classmethod
    def _add_sent(cls, text: str, *, embed: Embed = None, delete_after: float = None):
        print("Saved message")
        cls.sent_queue.put({"text": text, "embed": embed, "delete_after": delete_after})

    @classmethod
    def get_oldest_embed(cls):
        return cls.sent_queue.get()["embed"]