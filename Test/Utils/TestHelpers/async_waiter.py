from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import Event
from typing import Optional


class Waiter:

    def __init__(self, wait_checker: WaitChecker, name: str = None):
        self._wait_checker = wait_checker
        self._event = Event()
        self.name = name or "waiter"

    async def start(self):
        await self._event.wait()
        self._wait_checker.finish(self)

    def finish(self):
        self._event.set()


class WaitChecker:

    def __init__(self):
        self.finished: list[Waiter] = []

    def finish(self, waiter: Waiter):
        self.finished.append(waiter)

    @property
    def first(self) -> Optional[Waiter]:
        if self.finished:
            return self.finished[0]
        return None

    @property
    def last(self) -> Optional[Waiter]:
        if self.finished:
            return self.finished[-1]
        return None
