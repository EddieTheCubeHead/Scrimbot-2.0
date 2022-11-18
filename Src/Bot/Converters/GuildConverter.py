__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Context
from hintedi import HinteDI

from Bot.Converters.ConverterBase import ConverterBase
from Database.DatabaseConnections.GuildConnection import GuildConnection


@HinteDI.singleton
class GuildConverter(ConverterBase):

    connection: GuildConnection = None

    @HinteDI.inject
    def __init__(self, connection: GuildConnection):
        super().__init__(connection)

    async def convert(self, ctx: Context, argument: str):
        return self.get_guild(int(argument))

    def get_guild(self, guild_id: int):
        return self.connection.get_guild(guild_id)

