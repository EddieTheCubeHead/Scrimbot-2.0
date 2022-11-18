from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.VoiceChannel import VoiceChannel


@HinteDI.singleton
class ScrimChannelManager:

    @staticmethod
    def enumerate_teams(voice_channels: list[VoiceChannel]):
        team = 1
        for voice_channel in voice_channels:
            if voice_channel.team_number is None:
                voice_channel.team_number = team
                team += 1
        voice_channels.sort(key=lambda x: x.team_number)
        return voice_channels
