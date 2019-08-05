import dbl
import os
import traceback
import asyncio
import aiohttp

import discord
from discord.ext import commands, tasks

class DiscordBotList(commands.Cog):
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

    @commands.command(name="dbl")
    async def dbl_(self, ctx):
        """Get some info about the DBL stats"""
        bot = await self.dblpy.get_bot_info()

        embed = discord.Embed(title="Server Pets DBL", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

        embed.add_field(name="Server Count", value=bot["server_count"], inline=False)
        embed.add_field(name="Monthly Upvotes", value=bot["monthlyPoints"], inline=False)
        embed.add_field(name="Current Upvotes", value=bot["points"], inline=False)
        embed.add_field(name="Certified", value=bot["certifiedBot"], inline=False)
        embed.add_field(name="Tags", value=', '.join(bot["tags"]), inline=False)

        return await ctx.send(embed=embed)

    @commands.command(name="vote")
    async def vote_(self, ctx):
        """Get the link to vote"""
        return await ctx.send(embed=discord.Embed(description="[Vote for Server Pets here](https://discordbots.org/bot/502205162694246412/vote)", colour=discord.Colour.blue()))

def setup(bot):
    bot.add_cog(DiscordBotList(bot))