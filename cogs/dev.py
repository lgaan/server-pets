import discord
from discord.ext import commands

import matplotlib.pyplot as plt

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="usage")
    async def usage(self, ctx):
        """Get usage"""
        plt.clf()
        plt.plot([v for v in _bot.usage.values()], [k for k in _bot.usage.keys()])

        plt.savefig("img/usage.png")

        return await _ctx.send(file=discord.File("img/usage.png"))
