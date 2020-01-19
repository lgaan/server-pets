import traceback

from datetime import datetime

import discord
from discord.ext import commands

from utils.managers.kennelmanager import KennelManager
from utils.managers.accountmanager import AccountManager
from utils.converters import KennelDate

from utils.checks import has_voted

class Kennel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = KennelManager(bot)
        self.accounts = AccountManager(bot)
    
    @commands.group(name="kennel", invoke_without_subcommand=True)
    @has_voted()
    async def kennel_(self, ctx):
        """Show a list of all your kenneled pets"""
        if ctx.subcommand_passed:
            return
        
        kennel = await self.manager.get_kennel(ctx.author.id)
        embed = discord.Embed(title=f"{ctx.author.name}'s kennel.", description="You have no kenneled pets." if not kennel else "", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

        if not kennel:
            return await ctx.send(embed=embed)
            
        for pet in kennel:
            embed.add_field(name="Name", value=pet.name)
            embed.add_field(name="Release Date", value=f'{pet.release_date.strftime(r"%d/%m/%Y")} (In format `d/m/y`)')
            embed.add_field(name="** **", value="** **")
        
        return await ctx.send(embed=embed)
    
    @kennel_.command(name="add")
    async def add_(self, ctx, time: KennelDate, *, pet):
        """Add a pet to the kennel"""
        account = await self.accounts.get_account(ctx.author.id)
        pet = pet.lower()

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`.")
        if not account.pets:
            return await ctx.send("You do not have any pets. To adopt one use `p-adopt`.")

        if not await self.accounts.get_pet_named(ctx.author.id, pet):
            return await ctx.send(f"You do not have a pet named {pet}. To adopt one use `p-adopt`.")
        
        pet = await self.accounts.get_pet_named(ctx.author.id, pet)

        if pet.kenneled:
            return await ctx.send("This pet is already in the kennel. To view your kennel use `p-kennel`.")
        
        price = await self.manager.get_price(pet.type, time.date()-datetime.utcnow().date())

        embed = discord.Embed(title="Kennel", colour=discord.Colour.blue(), description=f"Are you sure you want to kennel this pet? It will cost you ${price}\nTo confirm react with <:greenTick:596576670815879169>, to cancel use <:redTick:596576672149667840>.", timestamp=ctx.message.created_at)

        bot_msg = await ctx.send(embed=embed)

        await bot_msg.add_reaction(":greenTick:596576670815879169")
        await bot_msg.add_reaction(":redTick:596576672149667840")

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=600,
                                                check=lambda r, u: u == ctx.author and str(r.emoji) in [
                                                    "<:greenTick:596576670815879169>",
                                                    "<:redTick:596576672149667840>"])
            if str(reaction.emoji) == "<:greenTick:596576670815879169>":
                await bot_msg.delete()
            else:
                await bot_msg.delete()
                return await ctx.send("Canceled.")
        except asyncio.TimeoutError:
            return await ctx.send("Time ran out.")

        if account.balance - price <= 0:
            return await ctx.send("You have not got enough money to do this.")
            
        await self.manager.add_pet(ctx.author.id, pet.name, time)
        await self.manager.charge_account(account, price)

        return await ctx.send(f"Your pet {pet.name} has been added to your kennel. To view your kennel use `p-kennel`, or to remove this pet use `p-kennel remove {pet.name}`")

    @kennel_.command(name="remove")
    async def remove_(self, ctx, *, pet):
        """Remove a pet from the kennel"""
        try:
            pet = pet.lower()

            account = await self.accounts.get_account(ctx.author.id)

            if not account:
                return await ctx.send("You do not have an account. To make one use `p-create`.")

            if not account.pets:
                return await ctx.send("You do not have any pets. To adopt one use `p-adopt`.")

            if not await self.accounts.get_pet_named(ctx.author.id, pet):
                return await ctx.send(f"You do not have a pet named {pet}. To adopt one use `p-adopt`.")
            
            pet = await self.accounts.get_pet_named(ctx.author.id, pet)

            if not pet.kenneled:
                return await ctx.send("This pet is not in the kennel. To view your kennel use `p-kennel`.")
            
            price = 500

            kennel = await self.manager.get_pet(ctx.author.id, pet.name)

            if kennel.overdue:
                return await ctx.send("Your pet is ready to collect, to collect them use `p-kennel collect`")

            embed = discord.Embed(title="Remove a pet", colour=discord.Colour.blue(), description=f"Are you sure you want to remove this pet from the kennel this pet? It will cost you ${price}\nTo confirm react with <:greenTick:596576670815879169>, to cancel use <:redTick:596576672149667840>.", timestamp=ctx.message.created_at)

            bot_msg = await ctx.send(embed=embed)

            await bot_msg.add_reaction(":greenTick:596576670815879169")
            await bot_msg.add_reaction(":redTick:596576672149667840")

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600,
                                                    check=lambda r, u: u == ctx.author and str(r.emoji) in [
                                                        "<:greenTick:596576670815879169>",
                                                        "<:redTick:596576672149667840>"])
                if str(reaction.emoji) == "<:greenTick:596576670815879169>":
                    await bot_msg.delete()
                else:
                    await bot_msg.delete()
                    return await ctx.send("Canceled.")
            except asyncio.TimeoutError:
                return await ctx.send("Time ran out.")
            
            if account.balance - price <= 0:
                return await ctx.send("You have not got enough money to do this.")
                
            await self.manager.charge_account(account, price)
            await self.manager.remove_pet(ctx.author.id, pet.name)

            return await ctx.send(f"Your pet {pet.name} was removed from the kennel.")
        except Exception:
            traceback.print_exc()
    
    @kennel_.command(name="collect")
    async def collect_(self, ctx, *, pet):
        """Collect a pet from the kennel"""
        pet = pet.lower()

        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`.")

        if not account.pets:
            return await ctx.send("You do not have any pets. To adopt one use `p-adopt`.")

        if not await self.accounts.get_pet_named(ctx.author.id, pet):
            return await ctx.send(f"You do not have a pet named {pet}. To adopt one use `p-adopt`.")
        
        pet = await self.accounts.get_pet_named(ctx.author.id, pet)

        if not pet.kenneled:
            return await ctx.send("This pet is not in the kennel. To view your kennel use `p-kennel`.")
        
        kennel = await self.manager.get_pet(ctx.author.id, pet.name)

        if not kennel.overdue:
            return await ctx.send(f"This pet has not finished its time in the kennel. To take it out early, use `p-kennel remove {pet.name}`") 
        
        await self.manager.remove_pet(ctx.author.id, pet.name)

        return await ctx.send(f"You have collected {pet.name} from the kennel.")
        

def setup(bot):
    bot.add_cog(Kennel(bot))