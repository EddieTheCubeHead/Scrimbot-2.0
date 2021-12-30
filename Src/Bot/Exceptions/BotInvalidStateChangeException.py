__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotInvalidStateChangeException(BotBaseRespondToContextException):

    def __init__(self, original_state: ScrimState, new_state: ScrimState):
        super().__init__(f"Could not move a scrim that is {original_state.description} into the state "
                         f"'{new_state.description}'.")
