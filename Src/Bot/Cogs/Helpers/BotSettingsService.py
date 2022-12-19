__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Guild
from hintedi import HinteDI

from Src.Bot.Converters.GuildConverter import GuildConverter
from Src.Configs.Config import Config


@HinteDI.singleton
class BotSettingsService:

    @HinteDI.inject
    def __init__(self, config: Config, guild_converter: GuildConverter):
        self.config = config
        self.guild_converter = guild_converter

    def get_deletion_time(self, guild: Guild) -> int:
        """A method that returns the idle scrim deletion time for a given guild."""

        guild_data = self.guild_converter.get_guild(guild.id)
        return guild_data.scrim_timeout or self.config.default_timeout
