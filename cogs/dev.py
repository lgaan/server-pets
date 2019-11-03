import discord
from discord.ext import commands

import traceback

from datetime import datetime
import matplotlib.pyplot as plt
import collections

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="usage")
    async def usage(self, ctx):
        """Get usage"""
        plt.clf()

        usage = collections.OrderedDict(sorted(self.bot.usage.items(), key=lambda kv: kv[1], reverse=True))

        plt.bar([k for k in usage.keys()], [v for v in usage.values()])

        plt.ylabel("Usage"); plt.xlabel("Commands")
        plt.xticks(rotation=90)
        plt.savefig("img/usage.png")

        return await ctx.send(file=discord.File("img/usage.png"))
    
    @commands.command(name="ug")
    async def user_growth_(self, ctx):
        """Get user growth"""
        try:
            plt.clf()
            
            plt.plot([x.split(" ")[1] for x in self.bot.ug.keys()], [x for x in self.bot.ug.values()])
            
            plt.ylabel("Users"); plt.xlabel("Date")
            plt.xticks(rotation=90)
            plt.savefig("img/ug.png")
            
            return await ctx.send(file=discord.File("img/ug.png"))
        except Exception:
            traceback.print_exc()
        
        
    @commands.command(name="raise")
    async def raise_(self, ctx):
        """Raise an error"""
        raise commands.CommandError("Raised")

def setup(bot):
    bot.add_cog(Dev(bot))