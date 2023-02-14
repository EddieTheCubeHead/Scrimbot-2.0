__version__ = "0.2"
__author__ = "Eetu Asikainen"

from discord import Guild

from Src.Bot.DataClasses.Scrim import Scrim


class ScrimVoiceOperationService:

    async def try_move_to_voice(self, guild: Guild, scrim: Scrim) -> bool:
        if not self._all_in_voice(guild, scrim):
            return False
        for participant_team in scrim.teams:
            channel = await guild.get_channel(participant_team.team.channel_id)
            for player in participant_team.team.members:
                member = await guild.get_member(player.user_id)
                await member.move_to(channel)
        return True

    @staticmethod
    def _all_in_voice(guild, scrim) -> bool:
        for participant_team in scrim.teams:
            for player in participant_team.team.members:
                if player.voice is None:
                    return False
                if player.voice.channel is None:
                    return False
                if player.voice.channel.guild.id != guild.id:
                    return False
        return True
