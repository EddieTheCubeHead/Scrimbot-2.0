import discord
from discord.ext import commands

class Scrim():

    all_scrims = {}

    def __init__(self, channel: discord.TextChannel):
        self.channel = channel
        self.all_scrims[channel.id] = self
        self.prefix = "/" # TODO dynamic prefix via database and settings

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str):

        if ctx.channel.id not in self.all_scrims:
            raise commands.BadArgument(f"This channel is not registered for scrim usage. \
             Ask a server admin to register it with '{self.prefix}register'  \
             or use an already registered channel.")
        
        
