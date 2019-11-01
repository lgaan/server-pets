import discord
from discord.ext import commands, tasks

from datetime import datetime

class Trackers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.tracker.start()
    
    @tasks.loop(hours=1)
    async def tracker(self):
        """Handle trackers"""
        users = len(self.bot.users)
        
        self.bot.ug[datetime.now().strftime(r"%Y-%M-%d %H:%M:%S")] = users
    
    @tracker.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Trackers(bot))