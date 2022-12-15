__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.DataClasses.VoiceChannel import VoiceChannel
from Src.Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


def _get_channel_name(voice_channel: VoiceChannel) -> str:
    return f"Team {voice_channel.team_number} voice" if voice_channel.team_number else "Voice lobby"


def _create_channel_mention(channel_id):
    return f"<#{channel_id}>"


# noinspection PyMethodMayBeStatic
@HinteDI.instance
class ScrimChannelEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, scrim_channel: ScrimChannel) -> Embed:
        description = "Channel data:"
        embed = Embed(title="New scrim channel registered successfully!", description=description)
        embed.add_field(name="Text channel", value=_create_channel_mention(scrim_channel.channel_id))
        for voice_channel in scrim_channel.voice_channels:
            embed.add_field(name=_get_channel_name(voice_channel),
                            value=_create_channel_mention(voice_channel.channel_id))
        return embed
