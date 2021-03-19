__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Src.Bot.ScrimClient import ScrimClient
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.ScrimState import ScrimState

def free_scrim():
    async def predicate(ctx: commands.Context):
        scrim = await Scrim.get_scrim(ctx)
        if not scrim.state == ScrimState.INACTIVE:
            raise commands.CheckFailure("There is already a scrim underway on this channel. Try another channel.")
        return True
    return commands.check(predicate)

def active_scrim():
    async def predicate(ctx: commands.Context):
        scrim = await Scrim.get_scrim(ctx)
        if ctx.author != scrim.master:
            raise commands.CheckFailure("Only the scrim creator can do that.")
        elif scrim.state == ScrimState.INACTIVE:
            raise commands.CheckFailure("That command requires an active scrim on the channel.")
        return True
    return commands.check(predicate)