import traceback
import random
import json
import asyncio

import discord
from discord.ext import commands, tasks

class AccountManager(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

        self.earning_rates = {
            "dog": 30,
            "cat": 30,
            "mouse": 15,
            "snake": 50,
            "spider": 50,
            "bird": 30,
            "horse": 100
        }

        self.earning_rates_fun = {
            "dog": 99999999,
            "cat": 99999999,
            "mouse": 99999999,
            "snake": 99999999,
            "spider": 99999999,
            "bird": 99999999,
            "horse": 99999999
        }

        self.managment.start()

    @tasks.loop(minutes=10.0)
    async def managment(self):
        """Gives an account certain amounts of money via their pets"""
        try:
            accounts = await self._bot.db.fetch("SELECT * FROM accounts")

            for account in accounts:
                if account["pets"]:
                    earning = sum(self.earning_rates[pet] for pet in account["pets"])

                    await self._bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account["balance"]+earning, account["owner_id"])
        except Exception:
            traceback.print_exc()
    
    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()

def setup(bot):
    bot.add_cog(AccountManager(bot))
