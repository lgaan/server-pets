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

class Handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.guild is None:
            return await ctx.send("Commands should be done in guilds")

        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        
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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print("g j")
        try:    
            embed = discord.Embed(title="Guild joined", colour=discord.Colour.blue(), timestamp=guild.me.joined_at)
            embed.add_field(name="Name", value=guild.name, inline=False)
            embed.add_field(name="Member Count", value=guild.member_count, inline=False)
            embed.add_field(name="Bot Count", value=len([m for m in guild.members if m.bot]), inline=False)

            embed.add_field(name="** **", value="** **", inline=False)

            embed.add_field(name="New Guild Count", value=len(self.bot.guilds), inline=False)
            embed.add_field(name="New Member Count", value=len(self.bot.users), inline=False)
            
            embed.add_field(name="Potential Bot Farm?", value="Yes" if sum(m for m in guild.members if m.bot) > 100 else "No", inline=False)

            embed.set_thumbnail(url=guild.icon_url)

            return await self.bot.get_channel(615299190485942292).send(embed=embed)
        except Exception:
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print("g r")
        try:
            embed = discord.Embed(title="Guild Left", colour=discord.Colour.blue(), timestamp=datetime.now())
            embed.add_field(name="Name", value=guild.name, inline=False)
            embed.add_field(name="Member Count", value=guild.member_count, inline=False)
            embed.add_field(name="Bot Count", value=len([m for m in guild.members if m.bot]), inline=False)

            embed.add_field(name="** **", value="** **", inline=False)

            embed.add_field(name="New Guild Count", value=len(self.bot.guilds), inline=False)
            embed.add_field(name="New Member Count", value=len(self.bot.users), inline=False)

            embed.add_field(name="Potential Bot Farm?", value="Yes" if sum(m for m in guild.members if m.bot) > 100 else "No", inline=False)

            embed.set_thumbnail(url=guild.icon_url)

            return await self.bot.get_channel(615299190485942292).send(embed=embed)
        except Exception:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Handlers(bot))
