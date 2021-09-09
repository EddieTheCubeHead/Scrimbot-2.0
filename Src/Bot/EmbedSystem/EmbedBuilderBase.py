__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from discord import Embed

from Bot.DataClasses.Displayable import Displayable


T = TypeVar('T', bound=Displayable)  # pylint: disable=invalid-name


# noinspection PyMethodMayBeStatic
class EmbedBuilderBase(ABC, Generic[T]):

    @abstractmethod
    def build(self, displayable: T) -> Embed:  # pragma: no-cover
        pass
