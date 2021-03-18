import discord
from discord.ext import commands

class ScrimCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
