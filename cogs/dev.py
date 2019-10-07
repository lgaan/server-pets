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

        plt.use("Agg")
        plt.bar([k for k in self.bot.usage.keys()], [v for v in self.bot.usage.values()])

        plt.ylabel("Commands"); plt.xlabel("Usage")
        plt.xticks(rotation=90)
        plt.savefig("img/usage.png")

        return await ctx.send(file=discord.File("img/usage.png"))

def setup(bot):
    bot.add_cog(Dev(bot))