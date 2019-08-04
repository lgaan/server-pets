import random
import string
import json

import asyncio

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

        if isinstance(error, commands.CommandNotFound):
            return
        
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

                tickets = await self.bot.db.fetch("SELECT * FROM tokens")

                if tickets:
                    data = json.loads(tickets[0]["token_values"])
                    data[code] = str(error)

                    await self.bot.db.execute("UPDATE tokens SET token_values = $1", json.dumps(data))
                else:
                    data = {}
                    data[code] = str(error)

                    await self.bot.db.execute("INSERT INTO tokens (token_values) VALUES ($1)", json.dumps(data))

                
                return await bot_msg.edit(embed=ticket)

        except asyncio.TimeoutError:
            return


def setup(bot):
    bot.add_cog(Handlers(bot))
