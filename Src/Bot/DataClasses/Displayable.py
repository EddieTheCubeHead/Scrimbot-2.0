__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import abstractmethod

from discord import Embed


class Displayable:  # pragma: no cover

    @abstractmethod
    def build(self, embed_builder) -> Embed:
        pass
