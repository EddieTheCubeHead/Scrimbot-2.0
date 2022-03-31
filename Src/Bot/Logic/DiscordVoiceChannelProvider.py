__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Exceptions.BuildException import BuildException
from Bot.Logic.DiscordObjectProvider import DiscordObjectProvider


@BotDependencyInjector.singleton
class DiscordVoiceChannelProvider(DiscordObjectProvider):

    def get_channel(self, channel_id: int):
        if not self.client:
            raise BuildException("Tried to fetch a channel from channel provider but the provider client was not set. "
                                 "Please ensure bot initialization is working correctly.")
        return self.client.get_channel(channel_id)

