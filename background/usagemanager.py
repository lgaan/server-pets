import traceback
import json

import discord
from discord.ext import commands, tasks

class UsageManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.managment.start()

        self.loop_index = 0

    @tasks.loop(minutes=10)
    async def managment(self):
        """Manage the bot usage"""

        old_usage = await self.bot.db.fetch("SELECT * FROM usage")

        if self.loop_index == 0:
            self.bot.usage = json.loads(old_usage[0]["usage_json"])
            
            self.loop_index += 1

        else:
            new_usage = {}

            for command, uses in json.loads(old_usage[0]["usage_json"]).items():
                if command in self.bot.usage.keys():
                    new_usage[command] = self.bot.usage[command] + uses
                else:
                    continue           
            try:
                await self.bot.db.execute("UPDATE usage SET usage_json = $1", json.dumps(new_usage))
            except Exception as e:
                traceback.print_exc()     
        return

    @managment.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(UsageManager(bot))
