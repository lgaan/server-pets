import traceback
import os
import asyncpg
import discord
import json

from discord.ext import commands
from pathlib import Path
from utils.paginator import EmbedPaginator


class BotContext(commands.Context):
    async def paginate(self, **kwargs):
        """Paginate a message"""
        message = kwargs.get("message")
        entries = kwargs.get("entries")

        paginator = EmbedPaginator(ctx=self, message=message, entries=entries)

        return await paginator.paginate()

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        if content is not None:
            content = await commands.clean_content().convert(self, content)
        return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce) 


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="p-", case_insensitive=True)
        self.remove_command("help")
        self.load_extension("jishaku")

        self.db = None

        self.usage = {}
        self.shop = {}

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=BotContext)
    
    async def load_from_folder(self, folder):           
        for ext in os.listdir(f"{folder}"):
            if ext.startswith("__"):
                continue

            module = f"{folder}.{ext.replace('/','.').replace('.py', '')}"

            try:
                self.load_extension(module)
                print(f"Loaded extension: {module}")
            except commands.ExtensionAlreadyLoaded:
                self.reload_extension(module)
                print(f"Reloaded extension: {module}")

            except commands.NoEntryPointError:
                print(f"Extension: {ext} does not have a setup function")

    async def set_codecs(self, pool):
        await pool.set_type_codec(
            "json",
            encoder=json.dumps,
            decoder=json.loads,
            schema="pg_catalog"
        )

    async def on_connect(self):
        credentials = dict(
            host=os.environ.get("DATABASE_HOST"),
            database=os.environ.get("DATABASE"),
            user=os.environ.get("PG_NAME"),
            password=os.environ.get("PG_PASSWORD"),
            init=self.set_codecs
        )
        self.db = await asyncpg.create_pool(**credentials)
        await self.load_from_folder("cogs")
              
    async def on_ready(self):
        await self.load_from_folder("background")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="p-help | Pets"))
        
        print("Connected")

    async def on_command(self, ctx):
        try:
            self.usage[ctx.command.name] += 1
        except KeyError:
            self.usage[ctx.command.name] = 1

    async def logout(self):
        await self.db.close()
        await super().logout()

if __name__ == "__main__":
    Bot().run(os.environ.get("TOKEN"), reconnect=True)
