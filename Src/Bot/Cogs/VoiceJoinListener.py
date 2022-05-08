__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime

import discord
from discord.ext import commands, tasks

from Bot.Cogs.Helpers.WaitingScrimService import WaitingScrimService
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Bot.Logic.ScrimManager import ScrimManager
from Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider


class VoiceJoinListener(commands.Cog):
    """A cog responsible for listening for voice joins and updating scrims waiting for players to join voice channels

    Listeners
    ---------

    scrim_player_voice_state_change_listener(member, before, after)
        A listener for scrim players changing voice state
    """

    @BotDependencyInjector.inject
    def __init__(self, participant_manager: ScrimParticipantProvider, waiting_scrim_service: WaitingScrimService,
                 response_builder: ScrimEmbedBuilder):
        self._participant_manager = participant_manager
        self._response_builder = response_builder
        self.waiting_scrims_service = waiting_scrim_service

    @commands.Cog.listener("on_voice_state_update")
    async def scrim_player_voice_state_change_listener(self, member: discord.Member, before: discord.VoiceState,
                                                       after: discord.VoiceState):
        if not self._participant_manager.try_get_participant(member.id) or not after.channel:
            return

        scrim = self.waiting_scrims_service.get_scrim(member)
        if scrim:
            await self._try_start_scrim(before, after, scrim)

    async def _try_start_scrim(self, before, after, scrim):
        if before.channel and before.channel.guild.id == scrim.message.channel.guild.id:
            return
        if after.channel.guild.id == scrim.message.channel.guild.id:
            if await scrim.start_with_voice():
                await self._handle_start(scrim)

    async def _handle_start(self, scrim):
        self.waiting_scrims_service.unregister(scrim)
        await self._response_builder.edit(scrim.message, displayable=scrim)
        await scrim.message.clear_reactions()

    @tasks.loop(seconds=5)
    async def prune_observers(self):
        for pruned_scrim in self.waiting_scrims_service.prune():
            await self._response_builder.edit(pruned_scrim.message, displayable=pruned_scrim)


def setup(client: ScrimBotClient):
    client.add_cog(VoiceJoinListener())
    print(f"Using cog {__name__}, with version {__version__}")
