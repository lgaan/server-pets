import traceback
import asyncio
import json
import random

import discord
from discord.ext import commands

from helpers.paginator import EmbedPaginator

class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pets = ["dog","cat","mouse","snake","spider","bird","horse"]

        self.pet_prices = {
            "dog": 500,
            "cat": 450,
            "mouse": 100,
            "snake": 750,
            "spider": 750,
            "bird": 250,
            "horse": 1500
        }

        self.water_rates = {
            1: "one bowl",
            2: "two bowls",
            3: "three bowls",
            4: "four bowls",
            5: "five bowls",
            6: "six bowls",
            7: "seven bowls"
        }

        self.pet_info = {
            "Dog": {"Price": 500, "Earns": 30, "Rarity": "Common"},
            "Cat": {"Price": 450, "Earns": 30, "Rarity": "Common"},
            "Mouse": {"Price": 100, "Earns": 15, "Rarity": "Common"},
            "Snake": {"Price": 750, "Earns": 50, "Rarity": "Uncommon"},
            "Spider": {"Price": 750, "Earns": 50, "Rarity": "Uncommon"},
            "Bird": {"Price": 250, "Earns": 30, "Rarity": "Uncommon"},
            "Horse": {"Price": 1500, "Earns": 100, "Rarity": "Rare"}
        }             

    @commands.command(name="adopt")
    async def adopt_(self, ctx, pet=None):
        """Shows a selection of the pets avaliable for the server. Leave `pet` empty for a list of pets."""
        if pet is None:
            embeds = []
            for key, value in self.pet_info.items():
                embed = discord.Embed(title=f"{ctx.guild}'s adoption centre. | {key}", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

                for info_key, info_value in value.items():
                    embed.add_field(name=info_key, value=f"${info_value}" if info_key in ["Earns","Price"] else info_value, inline=False)

                embed.set_thumbnail(url=ctx.guild.icon_url)

                embeds.append(embed)
            
            paginator = EmbedPaginator(ctx=ctx, message=None, entries=embeds)

            return await paginator.paginate()
        else:
            author_account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)

            if not author_account:
                return await ctx.send("You need an account to adopt an animal, to do so use the `p-create` command.")
            
            if author_account[0]["balance"] < self.pet_prices[pet.lower()]:
                return await ctx.send(f"You do not have enough cash to buy this pet. You can earn money by training your pet or competing in contests.")
            
            if pet.lower() in author_account[0]["pets"]:
                return await ctx.send(f"You already own a {pet.lower()}.")

            confirm_embed = discord.Embed(title="Confirm", description="Are you sure you want to adopt this animal?\nPlease react with <:greenTick:596576670815879169> to confirm, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            confirm_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

            bot_msg = await ctx.send(embed=confirm_embed)

            await bot_msg.add_reaction(":greenTick:596576670815879169")
            await bot_msg.add_reaction(":redTick:596576672149667840")

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=600, check=lambda r, u: u == ctx.author and str(r.emoji) in ["<:greenTick:596576670815879169>", "<:redTick:596576672149667840>"])
                if str(reaction.emoji) == "<:greenTick:596576670815879169>":
                    await bot_msg.delete()
                else:
                    await bot_msg.delete()
                    return await ctx.send("Canceled.")
            except asyncio.TimeoutError:
                return await ctx.send("Time ran out.")

            if author_account[0]["pets"]:
                author_account[0]["pets"].append(pet)
                pets = author_account[0]["pets"]
            else:
                pets = [pet]
            await self.bot.db.execute("UPDATE accounts SET balance = $1, pets = $2 WHERE owner_id = $3", author_account[0]["balance"]-self.pet_prices[pet], pets, ctx.author.id)
            
            embed = discord.Embed(title="Success!", description=f"You bought a {pet.lower()} for ${self.pet_prices[pet]}", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            embed.add_field(name="Old balance", value=f"${author_account[0]['balance']}")
            embed.add_field(name="New balance", value=f"${author_account[0]['balance']-self.pet_prices[pet]}")

        return await ctx.send(embed=embed)
    
    @commands.command(name="feed")
    async def feed_(self, ctx, pet):
        """Feed a pet a certain amount of food"""
        account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To create one please use `p-create`")
        
        if not account[0]["pets"]:
            return await ctx.send("You do not have any pets to feed. To adopt one please use `p-adopt`")
        
        if pet not in account[0]["pets"]:
            return await ctx.send(f"You do not own a {pet}. To buy one please say `p-adopt {pet}`")
        
        data = json.loads(account[0]["pet_bars"])
        items = json.loads(account[0]["items"])

        try:
            food = items[f"{pet.lower()} food"]
        except KeyError:
            return await ctx.send(f"It looks like you do not have any {pet.lower()} food. Please buy some using `p-buy {pet.lower()} food`")

        try:
            pet_hunger = data["hunger"][pet]
            amount_needed = 10 - pet_hunger

            if pet_hunger < 3:
                data["hunger"][pet] = data["hunger"][pet] + amount_needed

                await ctx.send(f"Your pet has gained {str(amount_needed)[:4]} hunger. It's health bar has changed to {str(data['hunger'][pet])[:4]}/10")

            else:
                amount = random.uniform(1.0, amount_needed)
                data["hunger"][pet] = data["hunger"][pet] + amount

                if data["hunger"][pet] > 10:
                    data["hunger"][pet] = 10

                await ctx.send(f"Your pet has gained {str(amount)[:4]} hunger. It's health bar has changed to {str(data['hunger'][pet])[:4]}/10")

            if (food - 1) <= 0:
                del items[f"{pet.lower()} food"]
            else:
                items[f"{pet.lower()} food"] = items[f"{pet.lower()} food"] - 1

            return await self.bot.db.execute("UPDATE accounts SET pet_bars = $1, items = $2 WHERE owner_id = $3", json.dumps(data), json.dumps(items),ctx.author.id)
        except KeyError:
            return await ctx.send(f"Your {pet} is on full hunger. You can check all of your pets' hunger and thirst bars using `p-pets`")
    
    @commands.command(name="water")
    async def water_(self, ctx, pet, amount:int=1):
        """Give a pet a certain amount of water. Default amount is 1"""
        account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To create one please use `p-create`")
        
        if not account[0]["pets"]:
            return await ctx.send("You do not have any pets to feed. To adopt one please use `p-adopt`")
        
        if pet not in account[0]["pets"]:
            return await ctx.send(f"You do not own a {pet}. To buy one please say `p-adopt {pet}`")
        
        data = json.loads(account[0]["pet_bars"])
        items = json.loads(account[0]["items"])

        try:
            water = items["water bowls"]
        except KeyError:
            return await ctx.send(f"It looks like you do not have any water. Please buy some using the `p-buy` command")

        if water <= 0:
            return await ctx.send(f"It looks like you do not have any water. Please buy some using the `p-buy` command")

        try:
            pet_thirst = data["thirst"][pet]
            amount_needed = 20 - pet_thirst

            if pet_thirst < 3:
                data["thirst"][pet] = data["thirst"][pet] + amount_needed

                await ctx.send(f"Your pet has gained {str(amount_needed)[:4]} thirst. It's thirst bar has changed to {str(data['thirst'][pet])[:4]}/20")
            else:
                amount = random.uniform(1.0, amount_needed)
                data["thirst"][pet] = data["thirst"][pet] + amount

                if data["thirst"][pet] > 20:
                    data["thirst"][pet] = 20

                await ctx.send(f"Your pet has gained {str(amount)[:4]} thirst. It's thirst bar has changed to {str(data['thirst'][pet])[:4]}/20")

            items["water bowls"] = items["water bowls"] - 1

            return await self.bot.db.execute("UPDATE accounts SET pet_bars = $1, items = $2 WHERE owner_id = $3", json.dumps(data), json.dumps(items), ctx.author.id)
        except KeyError:
            return await ctx.send(f"Your {pet} is on full hunger. You can check all of your pets' hunger and thirst bars using `p-pets`")
        

def setup(bot):
    bot.add_cog(Pets(bot))
