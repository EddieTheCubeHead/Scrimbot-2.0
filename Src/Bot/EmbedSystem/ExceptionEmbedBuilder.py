__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed
from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.EmbedSystem.ResponseBuilder import ResponseBuilder


@BotDependencyInjector.singleton
class ExceptionEmbedBuilder(ResponseBuilder):

    def build(self, ctx: Context, exception) -> Embed:
        title = "ScrimBot Error"
        embed = Embed(title=title, description=f"An error happened while processing command '{ctx.command.name}'")
        embed.add_field(name="Error message:", value=exception.message)
        if exception.send_help:
            embed.add_field(name="To get help:", value=exception.get_help_portion(ctx))
        embed.set_footer(text="If you think this behaviour is unintended, please report it in the bot repository in "
                              "GitHub at https://github.com/EddieTheCubeHead/Scrimbot-2.0")
        return embed
