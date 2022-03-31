__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime
from typing import Optional

from discord import Member

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Logic.ScrimManager import ScrimManager


@BotDependencyInjector.singleton
class WaitingScrimService:

    def __init__(self):
        self.waiting_scrims: dict[ScrimManager: datetime.datetime] = {}

    def register(self, scrim: ScrimManager):
        if scrim not in self.waiting_scrims:
            self.waiting_scrims[scrim] = datetime.datetime.now()

    def get_scrim(self, member: Member) -> Optional[ScrimManager]:
        for scrim in self.waiting_scrims.keys():
            if member.id in [participant.user_id for participant in scrim.teams_manager.all_participants]:
                return scrim

    def prune(self):
        prune_cutoff = datetime.datetime.now() - datetime.timedelta(minutes=5)
        pruned_scrims = []
        while len(self.waiting_scrims) > 0 and prune_cutoff > next(iter(self.waiting_scrims.values())):
            pruned_scrim = next(iter(self.waiting_scrims.keys()))
            pruned_scrim.cancel_voice_wait()
            self.waiting_scrims.pop(pruned_scrim)
            pruned_scrims.append(pruned_scrim)
        return pruned_scrims

