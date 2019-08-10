import traceback
import os
import asyncpg
import discord

from discord.ext import commands
from pathlib import Path
from helpers.paginator import EmbedPaginator


class BotContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_paginators = {}

    async def paginate(self, **kwargs):
        """Paginate a message"""
        if self.author.id in self.current_paginators.keys():
            await self.current_paginators[self.author.id].message.delete()
        
        message = kwargs.get("message")
        entries = kwargs.get("entries")

        Paginator = EmbedPaginator(ctx=self, message=message, entries=entries)

        self.current_paginators[self.author.id] = Paginator
        
        await Paginator.paginate()

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        if content is not None:
            content = await commands.clean_content().convert(self, content)
        return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce) 


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="p-", case_insensitive=True)
        self.remove_command("help")
        self.load_extension("jishaku")

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
                print(f"Extension: {ext.as_posix()} does not have a setup function")


    async def on_connect(self):
        credentials = dict(
            host=os.environ.get("DATABASE_HOST"),
            database=os.environ.get("DATABASE"),
            user=os.environ.get("PG_NAME"),
            password=os.environ.get("PG_PASSWORD")
        )
        self.db = await asyncpg.create_pool(**credentials)
        await self.load_from_folder("cogs")
        
        

    async def on_ready(self):
        await self.load_from_folder("background")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="p-help | Server Pets"))
        print("Connected")

    async def logout(self):
        await self.db.close()
        await super().logout()


if __name__ == "__main__":
    Bot().run(os.environ.get("TOKEN"), reconnect=True)
