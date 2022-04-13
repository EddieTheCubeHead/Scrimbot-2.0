__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Game import Game
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.Logic.ScrimManager import ScrimManager
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


def _create_voice_channels(scrim_channel):
    team_channels = list(filter(lambda channel: channel.team_number > 0, scrim_channel.voice_channels))
    lobby_channel = next((channel for channel in scrim_channel.voice_channels if channel.team_number == 0), None)
    return team_channels, lobby_channel


@BotDependencyInjector.singleton
class ActiveScrimsManager:

    def __init__(self):
        self.scrims: dict[int, ScrimManager] = {}

    def create_scrim(self, scrim_channel: ScrimChannel, game: Game) -> ScrimManager:
        team_channels, lobby_channel = _create_voice_channels(scrim_channel)
        teams_manager = ScrimTeamsManager(game, team_channels=team_channels, lobby=lobby_channel)
        created_scrim = ScrimManager(teams_manager)
        self.scrims[scrim_channel.channel_id] = created_scrim
        return created_scrim

    def try_get_scrim(self, channel_id: int):
        return self.scrims.get(channel_id, None)

    def drop(self, scrim: ScrimManager):
        self.scrims.pop(scrim.message.channel.id)
