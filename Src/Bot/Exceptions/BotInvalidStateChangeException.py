from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

from hintedi import HinteDI

from Src.Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
if TYPE_CHECKING:
    from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


class BotInvalidStateChangeException(BotBaseRespondToContextException):

    @HinteDI.inject
    def __init__(self, original_state: ScrimStateBase, new_state: ScrimStateBase, embed_builder: ExceptionEmbedBuilder):
        super().__init__(f"Could not move a scrim that is {original_state.description} into the state "
                         f"'{new_state.description}'.", embed_builder, delete_after=60)
