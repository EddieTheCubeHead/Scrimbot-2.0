__version__ = "ver"
__author__ = "Eetu Asikainen"

from functools import lru_cache

from discord.ext.commands import Context

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector

from Database.DatabaseConnections.GuildConnection import GuildConnection


@BotDependencyInjector.singleton
class GuildConverter(ConverterBase):

    connection: GuildConnection = None

    @BotDependencyInjector.inject
    def __init__(self, connection: GuildConnection):
        super().__init__(connection)

    async def convert(self, ctx: Context, argument: str):
        return self.get_guild(int(argument))

    @lru_cache
    def get_guild(self, guild_id: int):
        return self.connection.get_guild(guild_id)

