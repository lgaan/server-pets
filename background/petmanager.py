import traceback
import random
import json
import asyncio

import discord
from discord.ext import commands, tasks

class PetManager(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

        self.pet_hunger_rates = {
            "dog": (1.0,1.5),
            "cat": (1.5,2.0),
            "mouse": (1.0, 1.5),
            "snake": (1.25, 1.75),
            "spider": (1.0, 1.5),
            "bird": (1.0,2.0),
            "horse": (0.75,1.0)
        }
        self.pet_thirst_rates = {
            "dog": (0.5,0.75),
            "cat": (1.0,1.25),
            "mouse": (0.5,0.75),
            "snake": (0.5,0.75),
            "spider": (0.25,0.5),
            "bird": (1.0,1.25),
            "horse": (1.25,1.5)
        }

        self.managment.start()

    def cog_unload(self):
        self.managment.cancel()
    
    @tasks.loop(hours=1.0)
    async def managment(self):
        """Will decide if a pet gets hungry or thirsty"""
        accounts = await self._bot.db.fetch("SELECT * FROM accounts")

        for account in accounts:
            data = json.loads(account["pet_bars"])
            if account["pets"] != None:
                for pet in account["pets"]:
                    pet = pet.split(" ")[0]
                    # hunger
                    try:
                        hunger_rate = self.pet_hunger_rates[pet]
                        amount_to_take = random.uniform(hunger_rate[0],hunger_rate[1])

                        if pet in data["hunger"].keys() and (data["hunger"][pet] - amount_to_take) <= 0:
                            owner = self._bot.get_user(account["owner_id"])

                            await owner.send(f"Your {pet} was found to have not been fed in a long time. The animal rescue company has had to remove your pet.")

                            del data["hunger"][pet]
                            account["pets"].remove(pet)

                            if len(account["pets"]) == 0:
                                account["pets"] = None

                        if pet in data["hunger"].keys():
                            data["hunger"][pet] = data["hunger"][pet] - amount_to_take
                        else:
                            data["hunger"][pet] = (10.0 - amount_to_take)       

                        if data["hunger"][pet] < 3.0:
                            owner = self._bot.get_user(account["owner_id"])

                            await owner.send(f"Your {pet} has not been fed for a while, consider feeding it with the `p-feed {pet}` command.")
                    except Exception:
                        traceback.print_exc()

                    # thirst
                    try:
                        thirst_rate = self.pet_thirst_rates[pet]
                        amount_to_take = random.uniform(thirst_rate[0],thirst_rate[1])
                        
                        if pet in data["thirst"].keys() and (data["thirst"][pet] - amount_to_take) <= 0:
                            owner = self._bot.get_user(account["owner_id"])

                            await owner.send(f"Your {pet} was found to have not been watered in a long time. The animal rescue company has had to remove your pet.")

                            del data["thirst"][pet]
                            account["pets"].remove(pet)

                            if len(account["pets"]) == 0:
                                account["pets"] = None

                        if pet in data["thirst"].keys():
                            data["thirst"][pet] = data["thirst"][pet] - amount_to_take
                        else:
                            data["thirst"][pet] = (20.0 - amount_to_take)     

                        if data["thirst"][pet] < 3.0:
                            owner = self._bot.get_user(account["owner_id"])

                            await owner.send(f"Your {pet} has not drunk for a while, give it a drink with the `p-water {pet}` command.") 
                    except Exception:
                        traceback.print_exc()

            await self._bot.db.execute("UPDATE accounts SET pet_bars = $1, pets = $2 WHERE owner_id = $3", json.dumps(data), account["pets"], account["owner_id"])
    
    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()

def setup(bot):
    bot.add_cog(PetManager(bot))
                            
            