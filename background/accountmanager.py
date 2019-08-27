import traceback
import random
import json
import asyncio

import math

import discord
from discord.ext import commands, tasks

from utils.managers.accountmanager import AccountManager

class AccountEarnManager(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._manager = AccountManager(bot)

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

    async def get_points_needed(self, pet):
        """Will return the total amount of money earned needed to level up"""
        points = 0

        for level in range(0, pet.level):
            to_next = int(level + 300 * math.pow(2, float(level)/7))

            points += to_next
        
        return points

    @tasks.loop(minutes=30.0)
    async def managment(self):
        """Gives an account certain amounts of money via their pets"""
        try:
            accounts = await self._manager.get_all_accounts()

            for account in accounts:
                if self._bot.get_user(account.id) is None:
                    await self._bot.db.execute("DELETE FROM accounts WHERE owner_id = $1", account.id)
                    
                    continue
                                               
                if account.pets:
                    earning = sum((pet.earns*pet.level) for pet in account.pets)

                    for pet in account.pets:
                        if not pet.earned:
                            pet.earned = 0

                        needed = await self.get_points_needed(pet)

                        if (pet.earned+pet.earns) >= needed:
                            await self._bot.get_user(account.id).send(f"{pet.name} has levelled up to level {pet.level+1}! They now earn {pet.earns*(pet.level+1)} cash/30 minutes")
                            level = pet.level + 1
                        else:
                            level = pet.level
                        
                        await self._bot.db.execute("UPDATE pets SET earned = $1, level = $2 WHERE owner_id = $3 AND name = $4", (pet.earned+(pet.earns/pet.level)), level, account.id, pet.name)

                    await self._bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account.balance+earning, account.id)
        except Exception:
            traceback.print_exc()
    
    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()

def setup(bot):
    bot.add_cog(AccountEarnManager(bot))
