__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Member
from hintedi import HinteDI

from Src.Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Src.Bot.Logic.DiscordObjectProvider import DiscordObjectProvider


@HinteDI.singleton
class ScrimParticipantProvider(DiscordObjectProvider):

    def __init__(self):
        super().__init__()
        self.participants: dict[int: int] = {}

    def try_add_participant(self, participant: Member):
        self.ensure_not_participant(participant)
        self.participants[participant.id] = participant.guild.id

    def ensure_not_participant(self, participant: Member):
        if participant.id in self.participants:
            raise BotAlreadyParticipantException(participant)

    def try_get_participant(self, participant_id: int):
        if participant_id in self.participants:
            return self.client.get_guild(self.participants[participant_id]).get_member(participant_id)

    def drop_participants(self, *participant_ids: int):
        for participant_id in participant_ids:
            self._drop_participant(participant_id)

    def _drop_participant(self, participant_id: int):
        self.participants.pop(participant_id)
