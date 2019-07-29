import traceback
import os
import asyncpg

import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="p-", case_insensitive=True)
        self.remove_command("help")
        self.startup(["jishaku","cogs.pets","cogs.accounts","cogs.shop","cogs.misc","cogs.handlers"])
        self.db = self.loop.run_until_complete(self.create_pool())
    
    async def create_pool(self):
        return await asyncpg.create_pool(database=os.environ.get("DATABASE"), user=os.environ.get("PG_NAME"), password=os.environ.get("PG_PASSWORD"))

    def startup(self, cogs:list):
        for cog in cogs:
            try:
                self.load_extension(cog)
                print(cog)
            except Exception:
                traceback.print_exc()
    
    async def on_ready(self):
        self.startup(["background.petmanager","background.accountmanager"])
        print("Connected")

if __name__ == "__main__":
    Bot().run(os.environ.get("TOKEN"), reconnect=True)
