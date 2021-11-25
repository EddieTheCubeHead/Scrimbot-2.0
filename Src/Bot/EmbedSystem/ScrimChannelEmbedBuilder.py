__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


def _create_channel_mention(channel_id):
    return f"<#{channel_id}>"


# noinspection PyMethodMayBeStatic
@BotDependencyInjector.instance
class ScrimChannelEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, scrim_channel: ScrimChannel) -> Embed:
        description = "Channel data:"
        embed = Embed(title="New scrim channel registered successfully!", description=description)
        embed.add_field(name="Text channel", value=_create_channel_mention(scrim_channel.channel_id))
        for voice_channel in scrim_channel.voice_channels:
            embed.add_field(name=f"Team {voice_channel.team} voice" if voice_channel.team else "Voice lobby",
                            value=_create_channel_mention(voice_channel.channel_id))
        return embed
