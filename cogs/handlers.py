import traceback
import random
import string
import json
import os

from datetime import datetime
import asyncio

import aiohttp

import discord
from discord.ext import commands

from utils.checks import NotVoted

class Handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.guild is None:
            return await ctx.send("Commands should be done in guilds")

        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        
        if isinstance(error, NotVoted):
            embed = discord.Embed(title="Oops!", description="This command is for voters only! You can vote for me [here](https://top.gg/bot/502205162694246412/vote) to use this command. Note that it can take about a minute to update.", colour=discord.Colour.blue())
            return await ctx.send(embed=embed)
        
        await ctx.message.add_reaction("<:redTick:596576672149667840>")
        
        try:
            json = {
                "embeds": [{
                    "title": f"Error in {ctx.guild.name}, invocation: {ctx.command} {' '.join(list(ctx.args)[2:])}",
                    "description": f"More detailed summary has been logged.\n\n**Type**: {error.__class__.__name__}\n\n**Error**: {error}"
                }]
            }

            async with aiohttp.ClientSession() as cs:
                await cs.post(os.environ.get("ERROR_URL"), json=json)
        except Exception:
            traceback.print_exc()
        
        with open("log.txt", mode="a") as log:
            trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            log.write(f"\n\n{ctx.author} | {ctx.guild} | {ctx.command} {' '.join(list(ctx.args)[2:])}\nIgnoring exception in command {ctx.command}:\n{trace}\n----")
        
        embed = discord.Embed(title="Oops! An error has occured and the developer has been notified.", description=f"Want to know what went wrong? \n\n**{error.__class__.__name__}: {error}**", timestamp=ctx.message.created_at, colour=discord.Colour.blue())

        return await ctx.paginate(message=None, entries=[embed], delete_after=30)
        
def setup(bot):
    bot.add_cog(Handlers(bot))
