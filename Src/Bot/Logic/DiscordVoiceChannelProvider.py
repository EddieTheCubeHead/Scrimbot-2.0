__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

import discord

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Exceptions.BuildException import BuildException


@BotDependencyInjector.singleton
class DiscordVoiceChannelProvider:

    def __init__(self):
        self._client: Optional[discord.Client] = None

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value: discord.Client):
        if self._client:
            raise BuildException("Tried to set client for Discord voice channel provider while client was already set.")
        self._client = value

    def get_channel(self, channel_id: int):
        if not self._client:
            raise BuildException("Tried to fetch a channel from channel provider but the provider client was not set. "
                                 "Please ensure bot initialization is working correctly.")
        return self._client.get_channel(channel_id)

