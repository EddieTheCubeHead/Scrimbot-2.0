__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Src.Bot.Exceptions.BotBaseContextException import BotBaseContextException


class BotBaseRespondToContextException(BotBaseContextException, commands.CommandError):

    @HinteDI.inject
    def __init__(self, message: str, embed_builder: ExceptionEmbedBuilder, *, send_help: bool = True,
                 delete_after: float = None):
        self.message = message
        self.send_help = send_help
        self.delete_after = delete_after
        self._embed_builder = embed_builder

    async def resolve(self, ctx: Context):
        await self._embed_builder.send(ctx, displayable=self, delete_after=self.delete_after)

    @staticmethod
    def get_help_portion(ctx: commands.Context) -> str:
        return f"{ctx.prefix}help {ctx.command.name}"
