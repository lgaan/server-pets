import traceback
import os
import asyncpg

import discord
from discord.ext import commands

from helpers.paginator import EmbedPaginator

class BotContext(commands.Context):
    async def paginate(self, **kwargs):
        """Paginate a message"""
        message = kwargs.get("message")
        entries = kwargs.get("entries")

        Paginator = EmbedPaginator(ctx=self, message=message, entries=entries)

        return await Paginator.paginate()
    
    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        content = content.replace("@everyone","`@everyone`).replace("@here","`@here`")
        return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce) 

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="p-", case_insensitive=True)
        self.remove_command("help")
        self.startup(["jishaku","cogs.pets","cogs.accounts","cogs.shop","cogs.misc","cogs.setting","cogs.handlers"])
        self.db = self.loop.run_until_complete(self.create_pool())
    
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=BotContext)

    async def create_pool(self):
        return await asyncpg.create_pool(host=os.environ.get("DATABASE_HOST"), database=os.environ.get("DATABASE"), user=os.environ.get("PG_NAME"), password=os.environ.get("PG_PASSWORD"))

    def startup(self, cogs:list):
        for cog in cogs:
            try:
                self.load_extension(cog)
                print(cog)
            except Exception:
                traceback.print_exc()
    
    async def on_ready(self):
        self.startup(["background.petmanager","background.accountmanager","background.dbl"])

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="p-help | Server Pets"))
        print("Connected")

if __name__ == "__main__":
    Bot().run(os.environ.get("TOKEN"), reconnect=True)
