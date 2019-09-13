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

        self.pet_age = {
            "dog": {0: "puppy", 5: "adolescent", 10: "adult", 15: "elder"},
            "cat": {0: "kitten", 5: "adolescent", 10: "adult", 15: "elder"},
            "mouse": {0: "pup", 5: "adolescent", 10: "adult", 15: "elder"},
            "snake": {0: "hatchling", 5: "adolescent", 10: "adult", 15: "elder"},
            "spider": {0: "spiderling", 5: "adolescent", 10: "adult", 15: "elder"},
            "bird": {0: "chick", 5: "adolescent", 10: "adult", 15: "elder"},
            "horse": {0: "foal", 5: "adolescent", 10: "adult", 15: "elder"}
        }

        self.managment.start()

    async def get_points_needed(self, pet):
        """Will return the total amount of money earned needed to level up"""
        points = 0

        for level in range(0, pet.level):
            to_next = int(level + 300 * math.pow(2, float(level)/7))

            points += to_next
        
        return points

    async def get_next_level(self, level):
        """Get the next level to age"""
        rounded = 5 * round(level/5)

        if rounded <= level:
            rounded += 5
        
        return rounded

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
                    earning = 0 #sum((pet.earns*pet.level) for pet in account.pets)

                    for pet in account.pets:
                        earn = pet.earns*pet.level

                        earn *= self._bot.pet_species[pet.type][pet.species][1]

                        earning += earn / (pet.level * 2)

                        if not pet.earned:
                            pet.earned = 0

                        needed = await self.get_points_needed(pet)

                        if (pet.earned+pet.earns) >= needed and account.settings["dm_notifications"]:
                            await self._bot.get_user(account.id).send(f"{pet.name} has levelled up to level {pet.level+1}! They now earn {pet.earns*(pet.level+1)} cash/30 minutes")
                            level = pet.level + 1
                        else:
                            level = pet.level
                        
                        next_level = await self.get_next_level(pet.level) - 5

                        if pet.level == next_level and pet.age != self.pet_age[pet.type][next_level] and account.settings["dm_notifications"]:
                            await self._bot.get_user(account.id).send(f"{pet.name} has grown up! They are now a {self.pet_age[pet.type][next_level]}")

                            age = self.pet_age[pet.type][next_level] if next_level in self.pet_age[pet.type].keys() else "elder"
                        else:
                            age = pet.age
                        
                        await self._bot.db.execute("UPDATE pets SET earned = $1, level = $2, age = $3 WHERE owner_id = $4 AND name = $5", (pet.earned+(pet.earns/pet.level)), level, age, account.id, pet.name)

                    print(earning)
                    await self._bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account.balance+earning, account.id)
        except Exception:
            traceback.print_exc()
    
    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()

def setup(bot):
    bot.add_cog(AccountEarnManager(bot))