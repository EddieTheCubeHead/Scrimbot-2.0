__version__ = "0.1"
__author__ = "Eetu Asikainen"

from contextlib import contextmanager
from typing import Any
from unittest.mock import patch, MagicMock


class DiscordPatcher:

    def __init__(self):
        self.patches: list[tuple[str, Any]] = []
        self.patchers: list = []

    def add_patch(self, patched: str, mock: Any):
        self.patches.append((patched, mock))

    @contextmanager
    def patch_all(self):
        try:
            self.patchers.append(patch("Bot.Core.ScrimClient.ScrimClient.user", MagicMock()))
            for patched, mock in self.patches:
                self.patchers.append(patch(patched, mock))
            for patcher in self.patchers:
                patcher.start()
            yield
        finally:
            for patcher in self.patchers:
                patcher.stop()
