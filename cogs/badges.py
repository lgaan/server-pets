import discord
from discord.ext import commands

class Badges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_badge_complete(self, payload):
        print(payload)

def setup(bot):
    bot.add_cog(Badges(bot))