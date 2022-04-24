__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod


class BotBaseNoContextException(Exception, ABC):

    @abstractmethod
    async def resolve(self):  # pragma: no cover
        pass
