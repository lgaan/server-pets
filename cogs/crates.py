import discord
from discord.ext import commands

import random
import collections

from utils.managers.accountmanager import AccountManager

class Crates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.accounts = AccountManager(bot)
        
        self.crates = {
            "voter": [100, 100, 100, 1000, 1000, 1000, 10000],
            "basic": [100, 100, 100, 1000, 1000, 1000, 10000],
            "uncommon": [1000, 1000, 1000, 10000],
            "rare": [1000, 1000, 10000, 10000],
            "omega": [10000, 10000, 10000, 1000000]
        }
    
    @commands.Cog.listener()
    async def on_dbl_vote(self, payload):
        print(payload)
        account = await self.accounts.get_account(int(payload["user"]))
        
        if account:
            await account.add_key(self.bot, "voter")
    
    @commands.command(name="add-key")
    @commands.is_owner()
    async def add_key(self, ctx, *, key):
        account = await self.accounts.get_account(ctx.author.id)
        
        await account.add_key(self.bot, key)
        
        return await ctx.send(f"Added `1x {key}` to your inventory!")

    @commands.command(name="rem-key")
    @commands.is_owner()
    async def rem_key(self, ctx, *, key):
        account = await self.accounts.get_account(ctx.author.id)
        
        suc = await account.use_key(self.bot, key)
        
        if not suc:
            return await ctx.send("Oops, cant do that.")
        
        return await ctx.send(f"Removed `1x {key}` to your inventory!")
    
    @commands.command(name="keys")
    async def keys(self, ctx):
        """Check your keys"""
        account = await self.accounts.get_account(ctx.author.id)
        
        if not account:
            return await ctx.send("You dont have an account, make one using `p-create`.")
        
        desc = ""
        for key, count in list(collections.Counter(account.keys).items()):
            desc += f"`{count}x {key}`\n"
        
        embed = discord.Embed(title="Your keys", description=desc if desc != "" else "You don't have any keys. Want to get a free key? Simply vote for the bot [here](https://top.gg/bot/502205162694246412/vote)", colour=discord.Colour.blue())
        
        return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_dbl_test(self, payload):
        print(payload)
        account = await self.accounts.get_account(int(payload["user"]))
        
        if account:
            await account.add_key(self.bot, "voter")
        
    @commands.command(name="claim")
    async def claim_(self, ctx, crate):
        """Claim a vote bonus"""
        account = await self.accounts.get_account(ctx.author.id)
        
        if not account:
            return await ctx.send("You dont have an account, make one using `p-create`.")

        if crate.lower() in self.crates.keys():
            rewards = []
            money = 0
            
            if crate.lower() == "voter":
                keys = account.keys
                
                if "voter" not in account.keys:
                    return await ctx.send("You don't have any `voter` keys! To get this key, simply vote for the bot using: <https://top.gg/bot/502205162694246412/vote>")
                
                else:
                    # They can open the crate
                    value = random.choice(self.crates["voter"])
                    rewards.append(f"`${value}`")
                    money += value
                    
                    suc = await account.use_key(self.bot, "voter")
                    
                    if not suc:
                        return await ctx.send("Oops! Something went wrong.")
            else:
                keys = account.keys
                
                if crate.lower() not in keys:
                    return await ctx.send(f"You don't have any `{crate.lower()}` keys.")
                else:
                    value = random.choice(self.crates[crate.lower()])
                    rewards.append(f"`${value}`")
                    money += value
                    
                    suc = await account.use_key(self.bot, crate.lower())
                    
                    if not suc:
                        return await ctx.send("Oops! Something went wrong.")
                    
            embed = discord.Embed(title="Crate", description=f"You opened a {crate} crate and got {', '.join(rewards)}", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            embed.set_thumbnail(url="https://images.emojiterra.com/twitter/v12/512px/1f389.png")
            
            await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account.balance + money, ctx.author.id)
            return await ctx.send(embed=embed)
        else:
            crates = ', '.join([f"`{key}`" for key in self.crates.keys()])
            return await ctx.send(f"That crate doesnt exist. Choose from {crates}")

def setup(bot):
    bot.add_cog(Crates(bot))