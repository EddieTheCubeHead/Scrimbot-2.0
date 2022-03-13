__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Member

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException


@BotDependencyInjector.singleton
class ScrimParticipantManager:

    def __init__(self):
        self.participants: dict[int, Member] = {}

    def try_add_participant(self, participant: Member):
        self.ensure_not_participant(participant)
        self.participants[participant.id] = participant

    def ensure_not_participant(self, participant: Member):
        if participant.id in self.participants:
            raise BotAlreadyParticipantException(participant)

    def try_get_participant(self, participant_id: int):
        return self.participants[participant_id]
