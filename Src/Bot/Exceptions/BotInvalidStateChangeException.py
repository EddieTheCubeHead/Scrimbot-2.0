__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotInvalidStateChangeException(BotBaseRespondToContextException):

    @BotDependencyInjector.inject
    def __init__(self, original_state: ScrimState, new_state: ScrimState, embed_builder: ExceptionEmbedBuilder):
        super().__init__(f"Could not move a scrim that is {original_state.description} into the state "
                         f"'{new_state.description}'.", embed_builder, delete_after=60)
