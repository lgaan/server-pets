import traceback
import random
import string
import json

from datetime import datetime
import asyncio

import aiohttp

import discord
from discord.ext import commands

class Handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def create_token(self):
        return "".join([random.choice(string.ascii_letters) for x in range(10)])

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.guild is None:
            return await ctx.send("Commands should be done in guilds")

        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        
        await ctx.message.add_reaction("<:redTick:596576672149667840>")
        
        embed = discord.Embed(title="There was an error.", description="Are you able to solve this on your own? If yes react with <:greenTick:596576670815879169>, if not react with <:redTick:596576672149667840>", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=ctx.guild.me.avatar_url)

        embed.add_field(name="Error", value=error)

        bot_msg = await ctx.author.send(embed=embed)

        await bot_msg.add_reaction(":greenTick:596576670815879169")
        await bot_msg.add_reaction(":redTick:596576672149667840")

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=600, check=lambda r, u: u == ctx.author and str(r.emoji) in ["<:greenTick:596576670815879169>", "<:redTick:596576672149667840>"])
            if str(reaction.emoji) == "<:greenTick:596576670815879169>":
                return await bot_msg.delete()
            else:
                for reaction in bot_msg.reactions:
                    if ctx.guild.me in reaction.users:
                        await reaction.remove(ctx.guild.me)

                ticket = discord.Embed(title="There was an error.", description="Please visit the [support server](https://discord.gg/kayUTZm) and read the information channel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                ticket.set_thumbnail(url=ctx.guild.me.avatar_url)

                code = await self.create_token()
                ticket.add_field(name="Your Error Code", value=code)

                await self.bot.db.execute("INSERT INTO tokens (token, error) VALUES ($1,$2)", code, str(error))
                return await bot_msg.edit(embed=ticket)

        except asyncio.TimeoutError:
            return
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print("g j")
        try:    
            embed = discord.Embed(title="Guild joined", colour=discord.Colour.blue(), timestamp=guild.me.joined_at)
            embed.add_field(name="Name", value=guild.name, inline=False)
            embed.add_field(name="Member Count", value=guild.member_count, inline=False)
            embed.add_field(name="Bot Count", value=sum(m for m in guild.members if m.bot), inline=False)

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
            embed.add_field(name="Bot Count", value=sum(m for m in guild.members if m.bot), inline=False)

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
