import discord
import json

class ScrimClient(discord.Client):
    def __init__(self):
        super().__init__()
        with open("secrets.json") as secret_file:
            self.secrets = json.load(secret_file)

        self.run(self.secrets["token"])

    async def on_ready(self):
        print(f"Successfully logged in as {self.user.name}")

client = ScrimClient()