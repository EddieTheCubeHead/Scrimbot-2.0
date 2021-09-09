__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import abstractmethod

from discord import Embed


class Displayable:

    @abstractmethod
    def build(self, embed_builder) -> Embed:  # pragma: no-cover
        pass
