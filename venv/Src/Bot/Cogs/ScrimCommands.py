__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

class ScrimCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client: commands.Bot):
    print(f"Using cog {__name__}, version {__version__}")
    client.add_cog(ScrimCommands(client))