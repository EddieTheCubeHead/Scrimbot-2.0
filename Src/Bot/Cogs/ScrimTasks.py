__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from discord.ext import tasks

from Bot.Core.ScrimBotClient import ScrimBotClient


class ScrimTasks(commands.Cog):
    """A cog responsive for scrim related tasks

    Listeners
    ---------
    scrim_reaction_add_listener(react, user)
        A listener for processing added reactions

    scrim_reaction_remove_listener(react, user)
        A listener for processing removed reactions
    """
    def __init__(self, client: ScrimBotClient):
        """A constructor for the ScrimReactionListeners cog

        args
        ----

        :param client: The client instance associated with this cog
        :type client: ScrimBotClient
        """
        self._client = client

    @tasks.loop(seconds=5)
    async def try_waiting_voice_player_move(self):
        pass


def setup(client: ScrimBotClient):
    """A method for adding the cog to the bot

    args
    ----

    :param client: The instance of the bot the cog should be added into
    :type client: ScrimBotClient
    """

    client.add_cog(ScrimTasks(client))
    print(f"Using cog {__name__}, with version {__version__}")
