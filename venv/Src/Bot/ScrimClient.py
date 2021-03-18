import discord
import json
import logging
from discord.ext import commands
from Src.Bot.Cogs.ScrimCommands import ScrimCommands
from Src.Bot.Cogs.AdminCommands import AdminCommands
from Src.Database.DatabaseManager import DatabaseManager

class ScrimClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, intents = discord.Intents.default())

        # Logging setup code stolen from the original Scrim-Bot, that was probably stolen from somewhere else
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='scrim_bot.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

        self.add_cog(ScrimCommands(self))
        self.add_cog(AdminCommands(self))

        self.database_manager = DatabaseManager()

        with open("secrets.json") as secret_file:
            self.__secrets = json.load(secret_file)

        self.run(self.__secrets["token"])

    async def get_prefix(self, message: discord.Message):
        return "/"

    async def temp_msg(self, ctx: commands.Context, message: str, *, delete_delay = 8.0, delete_original_msg = True):
        temporary_message = await ctx.send(message)

        if delete_original_msg:
            try:
                await ctx.message.delete()
            except:
                pass

        await temporary_message.delete(delay=delete_delay)

    async def error_msg(self, ctx: commands.Context, error: BaseException, context_command):


    async def on_ready(self):
        print(f"Successfully logged in as {self.user.name}")

if __name__ == "__main__":
    client = ScrimClient()