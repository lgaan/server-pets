import dbl
import os
import traceback
import asyncio

import discord
from discord.ext import commands, tasks


class Dbl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dblpy = dbl.Client(bot, os.environ.get("DBL_TOKEN"))

        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        try:
            await self.dblpy.post_guild_count()
        except Exception as e:
            traceback.print_exc()
    
    @update_stats.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name="vote")
    async def vote_(self, ctx):
        """Get the link to vote"""
        return await ctx.send(embed=discord.Embed(description="[Vote for Server Pets here](https://discordbots.org/bot/502205162694246412/vote)", colour=discord.Colour.blue()))

def setup(bot):
    bot.add_cog(Dbl(bot))