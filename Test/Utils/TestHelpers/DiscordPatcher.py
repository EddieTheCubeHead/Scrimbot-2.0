__version__ = "0.1"
__author__ = "Eetu Asikainen"

from contextlib import contextmanager
from typing import Any
from unittest.mock import patch, MagicMock

from discord import CategoryChannel, TextChannel


class DiscordPatcher:

    def __init__(self):
        self.patches: list[tuple[str, Any]] = []
        self.patchers: list = []
        self._groups: list[CategoryChannel] = []

    def add_patch(self, patched: str, mock: Any):
        self.patches.append((patched, mock))

    def add_channel_group(self, channel_group: CategoryChannel):
        self._groups.append(channel_group)

    def try_add_group(self, channel: TextChannel):
        for group in self._groups:
            if channel.id in [candidate.id for candidate in group.voice_channels + group.text_channels]:
                channel.category_id = group.id
                channel.category = group

    @contextmanager
    def patch_all(self):
        try:
            self.patchers.append(patch("Src.Bot.Core.ScrimBotClient.ScrimBotClient.user", MagicMock()))
            for patched, mock in self.patches:
                self.patchers.append(patch(patched, mock))
            for patcher in self.patchers:
                patcher.start()
            yield
        finally:
            for patcher in self.patchers:
                patcher.stop()
