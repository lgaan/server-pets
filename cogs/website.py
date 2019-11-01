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
                
                data.append((u.name, balance, pets))
            
            balances = sorted(data, key=lambda k: k[1], reverse=True)
            pets = sorted(data, key=lambda k: k[2], reverse=True)
            
            async with aiohttp.ClientSession() as cs:
                async with cs.post("https://sp-webhost.herokuapp.com/api/lb", headers={"x-token": os.environ.get("API_TOKEN")}, json={"data": (balances, pets)}) as post:
                    print(await post.text())
                
            return await message.channel.send("Request for leaderboard has been sent.")

        if message.content == "stats":
            ctx = await self.bot.get_context(message)
            
            graphs = []
            
            for g in ["img/usage.png", "img/ug.png"]:
                f = discord.File(g)
                
                graphs.append(await ctx.send(file=f, delete_after=10))
            
            graphs = [g.attachments[0].url for g in graphs]
            
            async with aiohttp.ClientSession() as cs:
                async with cs.post("https://sp-webhost.herokuapp.com/api/stats", headers={"x-token": os.environ.get("API_TOKEN")}, json={"data": tuple(graphs)}) as post:
                    print(await post.text())
            
            return await message.channel.send("Request for stats has been sent.")
        

def setup(bot):
    bot.add_cog(Website(bot))