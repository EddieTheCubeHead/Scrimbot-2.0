__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Src.Bot.Exceptions.BotCheckFailure import BotCheckFailure


def free_scrim() -> callable(commands.Context):
    """A check that requires the channel to be eligible for scrims and not have a currently active scrim."""

    async def predicate(ctx: commands.Context):
        scrim = await ScrimChannel.get_scrim(ctx)
        if scrim is not None:
            raise BotCheckFailure("There is already an active scrim on the channel.")
        return True
    return commands.check(predicate)


def active_scrim():
    """A check that requires the channel to have an active scrim and the user to have permissions to that scirm."""

    async def predicate(ctx: commands.Context):
        scrim = await ScrimChannel.get_scrim(ctx)
        if scrim is None:
            raise BotCheckFailure("That command requires an active scrim on the channel.")
        if ctx.author != scrim.master:
            raise BotCheckFailure("Only the scrim creator can do that.")
        return True
    return commands.check(predicate)


def require_state(*valid_states: ScrimState):
    """A check that takes a list of valid scrim states and requires the scrim to be in one of them."""

    async def predicate(ctx: commands.Context):
        scrim = await ScrimChannel.get_scrim(ctx)
        if scrim.state not in valid_states:
            valid_state_explanation = "To use the command make sure the scrim is "
            if len(valid_states) == 1:
                valid_state_explanation += f"{valid_states[0]}."
            elif len(valid_states) == 2:
                valid_state_explanation += f"either {valid_states[0]} or {valid_states[1]}."
            else:
                valid_state_explanation += ", ".join(*valid_states[:-1])
                valid_state_explanation += f" or {valid_states[-1]}"
            raise BotCheckFailure(f"This command is not available when scrim is {scrim.state}.\n"
                                  f"{valid_state_explanation}")
        return True
    return commands.check(predicate)
