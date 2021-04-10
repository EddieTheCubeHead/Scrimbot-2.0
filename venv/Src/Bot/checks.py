__version__ = "0.1"
__author__ = "Eetu Asikainen"

"""A module containing the custom checks used by the bot."""

from discord.ext import commands

from Src.Bot.ScrimClient import ScrimClient
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.ScrimState import ScrimState
from Src.Bot.Exceptions.BotCheckFailure import BotCheckFailure

def free_scrim():
    """A check that requires the channel to be eligible for scrims and not have a currently active scrim."""

    async def predicate(ctx: commands.Context):
        scrim = await Scrim.get_scrim(ctx)
        if not scrim.state == ScrimState.INACTIVE:
            raise BotCheckFailure("There is already an active scrim on the channel.")
        ctx.scrim = scrim
        return True
    return commands.check(predicate)

def active_scrim():
    """A check that requires the channel to have an active scrim and the user to have permissions to that scirm."""

    async def predicate(ctx: commands.Context):
        scrim = await Scrim.get_scrim(ctx)
        if ctx.author != scrim.master:
            raise BotCheckFailure("Only the scrim creator can do that.")
        elif scrim.state == ScrimState.INACTIVE:
            raise BotCheckFailure("That command requires an active scrim on the channel.")
        ctx.scrim = scrim
        return True
    return commands.check(predicate)
