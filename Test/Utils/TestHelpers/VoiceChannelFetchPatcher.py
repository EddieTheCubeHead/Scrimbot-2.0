__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord


class VoiceChannelFetchPatcher:

    def __init__(self, *voice_channels: discord.VoiceChannel):
        self._voice_channels = {channel.id: channel for channel in voice_channels}

    def __call__(self, channel_id: int):
        if channel_id not in self._voice_channels:
            return None
        return self._voice_channels[channel_id]

    def add_mocked_channel(self, channel: discord.VoiceChannel):
        self._voice_channels[channel.id] = channel

    def remove_mocked_channel(self, channel_id: int):
        self._voice_channels.pop(channel_id)
