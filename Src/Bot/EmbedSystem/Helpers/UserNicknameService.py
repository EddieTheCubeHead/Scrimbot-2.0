__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord import Member, Guild
from discord.ext.commands import Context

from Bot.Core.BotCache import BotCache
from Bot.Core.BotDependencyInjector import BotDependencyInjector


@BotDependencyInjector.singleton
class UserNicknameService:

    def get_name(self, ctx: Context, user_id: int) -> str:
        member: Member = self.cached_get_name(ctx, user_id)
        return member.display_name

    @BotCache
    def cached_get_name(self, guild: Guild, user_id: int) -> Member:
        return discord.utils.get(guild.members, id=user_id)
