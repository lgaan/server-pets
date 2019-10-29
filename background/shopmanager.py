import traceback
import os

import aiohttp
import random

import discord
from discord.ext import commands, tasks

class ShopManager(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

        self.valid_items = {
            "carrots": {"price":20, "gain": 1},
            "potatoes": {"price":20, "gain": 1},
            "strawberries": {"price":15, "gain": 0.5},
            "mushrooms": {"price":20, "gain": 1},
            "tripe": {"price":40, "gain": 2},
            "steak": {"price":70, "gain": 5},
            "chicken": {"price":55, "gain": 3}
        }

        self.token = "logan"

        self._last_pull = None

        self.managment.start()

    @tasks.loop(hours=24)
    async def managment(self):
        try:
            new_items = {}
            
            incr = 0
            while incr < 5:
                item = random.choice(list(self.valid_items.keys()))

                if item not in new_items:
                    new_items[item] = self.valid_items[item]

                    incr += 1
                else:
                    continue

            self._bot.shop = new_items

            async with aiohttp.ClientSession() as cs:
                await cs.post(f"https://sp-webhost.herokuapp.com/api/shop", json={"items": new_items}, headers={"x-token": os.environ.get("API_TOKEN")})

        except Exception:
            traceback.print_exc()
    
    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()


def setup(bot):
    bot.add_cog(ShopManager(bot))
