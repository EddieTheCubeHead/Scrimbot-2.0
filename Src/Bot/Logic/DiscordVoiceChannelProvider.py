__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.Exceptions.BuildException import BuildException
from Src.Bot.Logic.DiscordObjectProvider import DiscordObjectProvider


@HinteDI.singleton
class DiscordVoiceChannelProvider(DiscordObjectProvider):

    def get_channel(self, channel_id: int):
        if not self.client:
            raise BuildException("Tried to fetch a channel from channel provider but the provider client was not set. "
                                 "Please ensure bot initialization is working correctly.")
        return self.client.get_channel(channel_id)

