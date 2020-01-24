import discord
from discord.ext import commands

import random

from utils.managers.accountmanager import AccountManager

class Crates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.accounts = AccountManager(bot)
        
        self.crates = {
            "voter": [100, 100, 100, 1000, 1000, 1000, 10000]
        }
    
    @commands.Cog.listener()
    async def on_dbl_vote(self, payload):
        print(payload)
        account = await self.accounts.get_account(int(payload["user"]))
        
        if account:
            await account.add_key("voter")
    
    @commands.command(name="keys")
    async def keys(self, ctx):
        """Check your keys"""
        account = await self.accounts.get_account(ctx.author.id)
        
        if not account:
            return await ctx.send("You dont have an account, make one using `p-create`.")
        
        keys = account.keys
        
        return await ctx.send(keys)

    @commands.Cog.listener()
    async def on_dbl_text(self, payload):
        print(payload)
        
    @commands.command(name="claim")
    async def claim_(self, ctx, crate):
        """Claim a vote bonus"""
        account = await self.accounts.get_account(ctx.author.id)
        
        if not account:
            return await ctx.send("You dont have an account, make one using `p-create`.")

        if crate.lower() in self.crates.keys():
            rewards = []
            
            if crate.lower() == "voter":
                voted = await self.bot.has_voted(ctx.author)
                
                if not voted:
                    return await ctx.send("You have not voted! In order to open this crate, please vote at <https://top.gg/bot/502205162694246412/vote>")
                
                else:
                    # They can open the crate
                    value = random.choice(self.crates["voter"])
                    rewards.append(f"`${value}`")
                    
            embed = discord.Embed(title="Crate", description=f"You opened a {crate} crate and got {', '.join(rewards)}", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            embed.set_thumbnail(url="https://images.emojiterra.com/twitter/v12/512px/1f389.png")
            return await ctx.send(embed=embed)
        else:
            crates = ', '.join([f"`{key}`" for key in self.crates.keys()])
            return await ctx.send(f"That crate doesnt exist. Choose from {crates}")

def setup(bot):
    bot.add_cog(Crates(bot))