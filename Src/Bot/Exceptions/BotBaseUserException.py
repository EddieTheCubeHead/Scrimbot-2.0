__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Bot.Exceptions.BotBaseException import BotBaseException


class BotBaseUserException(BotBaseException, commands.CommandError):

    @BotDependencyInjector.inject
    def __init__(self, message: str, embed_builder: ExceptionEmbedBuilder, *, send_help=True):
        self.message = message
        self.send_help = send_help
        self._embed_builder = embed_builder

    async def resolve(self, ctx: Context):
        await self._embed_builder.send(ctx, displayable=self)

    @staticmethod
    def get_help_portion(ctx: commands.Context) -> str:
        return f"{ctx.prefix}help {ctx.command.name}"
