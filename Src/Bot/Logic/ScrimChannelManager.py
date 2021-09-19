from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.VoiceChannel import VoiceChannel


@BotDependencyInjector.singleton
class ScrimChannelManager:

    @staticmethod
    def enumerate_teams(voice_channels: list[VoiceChannel]):
        team = 1
        for voice_channel in voice_channels:
            if voice_channel.team is None:
                voice_channel.team = team
                team += 1
        voice_channels.sort(key=lambda x: x.team)
        return voice_channels
