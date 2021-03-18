import discord
from discord.ext import commands

class Scrim():

    __all_scrims = {}

    def __init__(self, channel_id: int):
        self.__all_scrims[channel_id] = self

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str):

        if ctx.channel.id not in cls.__all_scrims:
            raise commands.BadArgument("This channel is not registered for scrim usage.")
        
        else:
            return cls.__all_scrims[ctx.channel.id]