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

        self.loop_index = 0

    def cog_unload(self):
        self.managment.cancel()
    
    @tasks.loop(hours=2)
    async def managment(self):
        """Will decide if a pet gets hungry or thirsty"""
        if self.loop_index = 0:
            # Check if the bot has just restarted to stop pets loosing stats upon restart 
            await asyncio.sleep(7200):
        self.loop_index += 1

        try:
            accounts = await self._bot.db.fetch("SELECT * FROM accounts")

            for account in accounts:
                if self._bot.get_user(account["owner_id"]) is None:
                    await self._bot.db.execute("DELETE FROM accounts WHERE owner_id = $1", account["owner_id"])
                    
                    continue
                                               
                data = json.loads(account["pet_bars"])
                settings = json.loads(account["settings"])
                                               
                if account["pets"] != None:
                    pets = json.loads(account["pets"])
                                               
                    for pet_type, pet_names in pets.items():
                        for pet_name in pet_names:
                            # hunger
                            try:
                                hunger_rate = self.pet_hunger_rates[pet_type]
                                amount_to_take = random.uniform(hunger_rate[0],hunger_rate[1])

                                if pet_name in data["hunger"].keys() and (data["hunger"][pet_name] - amount_to_take) <= 0:
                                    if settings["death_reminder"]:                               
                                        owner = self._bot.get_user(account["owner_id"])

                                        try:
                                            await owner.send(f"{pet_name} was found to have not been fed in a long time. The animal rescue company has had to remove your pet.")
                                        except discord.Forbidden:
                                            pass
                                            
                                    del data["hunger"][pet_name]
                                    pets[pet_type].remove(pet_name)

                                if pet_name in data["hunger"].keys():
                                    data["hunger"][pet_name] = data["hunger"][pet_name] - amount_to_take
                                else:
                                    data["hunger"][pet_name] = (10.0 - amount_to_take)       

                                if data["hunger"][pet_name] < 3.0 and settings["dm_notifications"]:
                                    owner = self._bot.get_user(account["owner_id"])

                                    await owner.send(f"{pet_name} has not been fed for a while, consider feeding it with the `p-feed {pet_name}` command.")
                                
                            except Exception:
                                traceback.print_exc()

                            # thirst
                            try:
                                thirst_rate = self.pet_thirst_rates[pet_type]
                                amount_to_take = random.uniform(thirst_rate[0],thirst_rate[1])
                                
                                if pet_name in data["thirst"].keys() and (data["thirst"][pet_name] - amount_to_take) <= 0:
                                    if settings["death_reminder"]:
                                        owner = self._bot.get_user(account["owner_id"])

                                        await owner.send(f"{pet_name} was found to have not been watered in a long time. The animal rescue company has had to remove your pet.")

                                    del data["thirst"][pet_name]
                                    pets[pet_type].remove(pet_name)

                                if pet_name in data["thirst"].keys():
                                    data["thirst"][pet_name] = data["thirst"][pet_name] - amount_to_take
                                else:
                                    data["thirst"][pet_name] = (20.0 - amount_to_take)     

                                if data["thirst"][pet_name] < 3.0 and settings["dm_notifications"]:
                                    owner = self._bot.get_user(account["owner_id"])

                                    await owner.send(f"{pet_name} has not drunk for a while, give it a drink with the `p-water {pet_name}` command.") 
                                
                            except Exception:
                                traceback.print_exc()

                    await self._bot.db.execute("UPDATE accounts SET pet_bars = $1, pets = $2 WHERE owner_id = $3", json.dumps(data), json.dumps(pets), account["owner_id"])
        
        except Exception:
            traceback.print_exc()
    
    @managment.before_loop
    async def before(self):
        await self._bot.wait_until_ready()

def setup(bot):
    bot.add_cog(PetManager(bot))
                            
            
