import traceback
import json

import discord
from discord.ext import commands, tasks

class UsageManager(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        
        self.managment.start()

        self.loop_index = 0

    @tasks.loop(seconds=10)
    async def managment(self):
        """Manage the bot usage"""
        old_usage = await self._bot.db.fetch("SELECT * FROM usage")

        if self.loop_index == 0:
            self._bot.usage = json.loads(old_usage[0]["usage_json"])
            
            self.loop_index += 1

        else:   
            try:
                await self._bot.db.execute("UPDATE usage SET usage_json = $1", self._bot.usage)
            except Exception as e:
                traceback.print_exc()     
        return

    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()

def setup(bot):
    bot.add_cog(UsageManager(bot))
