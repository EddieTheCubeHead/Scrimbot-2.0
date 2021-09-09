__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector


# this class is critical for making cogs easily testable and thus it's ok to have some static functions
# noinspection PyMethodMayBeStatic
@BotDependencyInjector.instance
class ResponseBuilder:

    async def send(self, ctx, text=None, *, embed_data=None, delete_after=None):
        if embed_data is None:
            await ctx.send(text, delete_after=delete_after)
        else:
            await ctx.send(text, embed=embed_data.build(), delete_after=delete_after)
