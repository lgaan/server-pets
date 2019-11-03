import discord
from discord.ext import commands

import os
import aiohttp

from utils.managers.accountmanager import AccountManager

class Website(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.accounts = AccountManager(bot)
        
        self.actions = {
            "leaderboard": self.accounts.get_lb_accounts
        }
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Used to detect website requests"""
        if message.channel.id != 615178303103565824:
            return
        
        if message.content == "leaderboard":
            ctx = await self.bot.get_context(message)
            
            _, leaderboard = await self.accounts.get_lb_accounts(ctx, lb_type="global")
            
            data = []
            
            for user in leaderboard[:5]:
                user = await self.accounts.get_account(user)
                
                u = self.bot.get_user(user.id)
                balance = user.balance
                
                pets = len(user.pets) if user.pets else 0
                
                data.append((u.name, balance, num))
            
            balances = sorted(data, key=lambda k: k[1], reverse=True)
            
            fetch = await self.bot.db.fetch("SELECT * FROM accounts")
            pets = []
            
            for account in fetch:
                account = await self.accounts.get_account(account["id"])

                if not account.pets:
                    continue
                
                user = self.bot.get_user(account.id)
                
                pets.append((user.name, len(account.pets), account.balance))
            
            pets = sorted(pets, key=lambda k: k[1], reverse=True) 
            
            async with aiohttp.ClientSession() as cs:
                async with cs.post("http://127.0.0.1:5000/api/lb", headers={"x-token": os.environ.get("API_TOKEN")}, json={"data": (balances, pets)}) as post:
                    print(await post.text())
                
            return await message.channel.send("Request for leaderboard has been sent.")
        

def setup(bot):
    bot.add_cog(Website(bot))