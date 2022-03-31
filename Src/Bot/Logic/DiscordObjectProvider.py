__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

import discord

from Bot.Exceptions.BuildException import BuildException


class DiscordObjectProvider:

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
