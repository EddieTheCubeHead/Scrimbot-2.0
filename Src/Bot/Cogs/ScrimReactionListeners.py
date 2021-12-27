__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Reaction, Member, DiscordException
from discord.ext import commands

from Bot.Converters.UserConverter import UserConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.User import User
from Bot.EmbedSystem.ScrimEmbedBuilder import ScrimEmbedBuilder
from Bot.Logic.ActiveScrimsManager import ActiveScrimsManager
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Src.Bot.DataClasses.ScrimState import ScrimState
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.DataClasses.ScrimChannel import ScrimChannel


class ScrimReactionListeners(commands.Cog):
    """A cog responsive for tracking the reaction-based UI of the scrims

    Listeners
    ---------
    scrim_reaction_add_listener(react, user)
        A listener for processing added reactions

    scrim_reaction_remove_listener(react, user)
        A listener for processing removed reactions
    """

    @BotDependencyInjector.inject
    def __init__(self, scrim_manager: ActiveScrimsManager, embed_builder: ScrimEmbedBuilder,
                 user_converter: UserConverter):
        self.scrim_manager = scrim_manager
        self.embed_builder = embed_builder
        self.user_converter = user_converter

    @commands.Cog.listener("on_reaction_add")
    async def scrim_reaction_add_listener(self, react: Reaction, user: Member):
        """A listener responsible for processing reactions added to scrim messages

        args
        ----

        :param react: The reaction associated with the event
        :type react: discord.Reaction
        :param user: The user associated with the reaction event
        :type user: discord.Member
        """
        if user.bot:
            return

        scrim = self.scrim_manager.try_get_scrim(react.message.channel.id)
        if not scrim:
            return

        try:
            if react.emoji == "\U0001F3AE" and scrim.state.name is ScrimState.LFP.name:
                scrim.teams_manager.add_player(ScrimTeamsManager.PARTICIPANTS,
                                               self.user_converter.get_user(user.id))

            elif react.emoji == "\U0001F441" and scrim.state.name is ScrimState.LFP.name:
                scrim.teams_manager.add_player(ScrimTeamsManager.SPECTATORS,
                                               self.user_converter.get_user(user.id))

            elif react.emoji == "1\u20E3" and scrim.state == ScrimState.LOCKED:
                await scrim.set_team_1(user)

            elif react.emoji == "2\u20E3" and scrim.state == ScrimState.LOCKED:
                await scrim.set_team_2(user)

            elif react.emoji == "\U0001F451" and scrim.state == ScrimState.CAPS_PREP:
                await scrim.add_captain(user)

            else:
                await react.remove(user)

        except DiscordException as exception:
            await react.remove(user)
            await self._client.handle_react_internal_error(react, user, exception)

        await self.embed_builder.edit(react.message, displayable=scrim)

    @commands.Cog.listener("on_reaction_remove")
    async def scrim_reaction_remove_listener(self, react: Reaction, user: Member):
        """A listener responsible for processing reactions removed from scrim messages

        args
        ----

        :param react: The reaction associated with the event
        :type react: discord.Reaction
        :param user: The user associated with the reaction event
        :type user: discord.Member
        """

        if user.bot:
            return

        scrim = await ScrimChannel.get_from_reaction(react)
        if not scrim:
            return

        try:
            if react.emoji == "\U0001F3AE" and scrim.state == ScrimState.LFP:
                await scrim.remove_player(user)

            elif react.emoji == "\U0001F441" and scrim.state == ScrimState.LFP:
                await scrim.remove_spectator(user)

            elif (react.emoji == "1\u20E3" or react.emoji == "2\u20E3") and scrim.state == ScrimState.LOCKED:
                await scrim.set_teamless(user)

            elif react.emoji == "\U0001F451" and scrim.state == ScrimState.CAPS_PREP:
                await scrim.remove_captain(user)

        except DiscordException as exception:
            await self._client.handle_react_internal_error(react, user, exception)


def setup(client: ScrimBotClient):
    """A method for adding the cog to the bot

    args
    ----

    :param client: The instance of the bot the cog should be added into
    :type client: ScrimBotClient
    """

    client.add_cog(ScrimReactionListeners())
    print(f"Using cog {__name__}, with version {__version__}")
