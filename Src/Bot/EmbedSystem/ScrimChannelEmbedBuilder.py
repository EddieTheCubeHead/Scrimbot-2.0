__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


def _create_channel_mention(channel_id):
    return f"<#{channel_id}>"


# noinspection PyMethodMayBeStatic
@BotDependencyInjector.instance
class ScrimChannelEmbedBuilder(ResponseBuilder):

    def build(self, scrim_channel: ScrimChannel) -> Embed:
        description = "Associated voice channels:" if scrim_channel.voice_channels else "No associated voice channels."
        embed = Embed(title=_create_channel_mention(scrim_channel.channel_id), description=description)
        for voice_channel in scrim_channel.voice_channels:
            embed.add_field(name=f"Team {voice_channel.team}" if voice_channel.team else "Lobby",
                            value=_create_channel_mention(voice_channel.channel_id))
        return embed
