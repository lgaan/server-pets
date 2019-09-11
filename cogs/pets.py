import traceback
import asyncio
import json
import random

from numpy import random as npr
from datetime import datetime

import discord
from discord.ext import commands

from utils.paginator import EmbedPaginator
from utils.converters import RenameConverter
from utils.managers.accountmanager import AccountManager

class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = AccountManager(bot)

        self.pets = ["dog", "cat", "mouse", "snake", "spider", "bird", "horse"]

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

        self.baby_names = {
            "dog": "puppy",
            "cat": "kitten",
            "mouse": "pup",
            "snake": "hatchling",
            "spider": "spiderling",
            "bird": "chick",
            "horse": "foal"
        }

    async def get_random_species(self, pet_type):
        """Get a random spicies"""
        species = self.bot.pet_species

        rand = npr.choice(list(species[pet_type]), p=[0.3, 0.2, 0.2, 0.2, 0.05, 0.05])

        return rand

    @commands.command(name="adopt")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def adopt_(self, ctx, pet=None):
        """Shows a selection of the pets avaliable for the server. Leave `pet` empty for a list of pets."""
        try:
            if pet is None:
                embeds = []
                for key, value in self.pet_info.items():
                    embed = discord.Embed(title=f"{ctx.guild}'s adoption centre. | {key}", colour=discord.Colour.blue(),
                                          timestamp=ctx.message.created_at)

                    for info_key, info_value in value.items():
                        embed.add_field(name=info_key,
                                        value=f"${info_value}" if info_key in ["Earns", "Price"] else info_value,
                                        inline=False)

                    embed.set_thumbnail(url=ctx.guild.icon_url)

                    embeds.append(embed)

                return await ctx.paginate(message=None, entries=embeds)
            else:
                account = await self.manager.get_account(ctx.author.id)

                if not account:
                    return await ctx.send(
                        "You need an account to adopt an animal, to do so use the `p-create` command.")

                if len(account.pets) > 100 and account.pets:
                    return await ctx.send("You have too many pets!")

                if pet.lower() not in self.pets:
                    return await ctx.send("That pet does not exist. To view a list of pets use `p-adopt`")

                if account.balance < self.pet_prices[pet.lower()]:
                    return await ctx.send(f"You do not have enough cash to buy this pet. You can earn money by "
                                          f"training your pet or competing in contests.")

                confirm_embed = discord.Embed(title="Confirm", description="Are you sure you want to adopt this "
                                                                           "animal?\nPlease react with "
                                                                           "<:greenTick:596576670815879169> to "
                                                                           "confirm, or <:redTick:596576672149667840> "
                                                                           "to cancel.", colour=discord.Colour.blue(

                ), timestamp=ctx.message.created_at)
                confirm_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

                bot_msg = await ctx.send(embed=confirm_embed)

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

                name_message = await ctx.send(embed=discord.Embed(title=f"Your {pet.lower()}",
                                                                  description=f"Your {pet.lower()} will need a name! Please reply to this message with the name of your pet.",
                                                                  colour=discord.Colour.blue(),
                                                                  timestamp=ctx.message.created_at))

                try:
                    message = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author == ctx.author)

                    if message:
                        await name_message.delete()
                except asyncio.TimeoutError:
                    return await ctx.send("Time ran out.")

                if "@everyone" in message.content or "@here" in message.content:
                    return await ctx.send("That pet name includes a blacklisted word. Please try again with another "
                                          "name.")

                if account.pets and message.content.lower() in [pet.name for pet in account.pets]:
                    return await ctx.send(f"You already own a pet named {message.content.lower()}, please re-use this command with an alternate name.")

                species = await self.get_random_species(pet.lower())

                await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2",
                                          account.balance - self.pet_prices[pet.lower()], ctx.author.id)

                await self.bot.db.execute("INSERT INTO pets (owner_id, name, type, thirst, hunger, earns, level, age, earned, species) VALUES ($1,"
                                          "$2,$3,20,10,$4,$5,$6,0,$7)", ctx.author.id, message.content.lower(), pet.lower(), self.pet_info[f"{pet[0].upper()}{pet[1:]}"]["Earns"], 1, self.baby_names[pet.lower()], species)

                embed = discord.Embed(title="Success!",
                                      description=f"You bought a {pet.lower()} for ${self.pet_prices[pet]} (With a species of {species})",
                                      colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                embed.add_field(name="Old balance", value=f"${account.balance}")
                embed.add_field(name="New balance", value=f"${account.balance - self.pet_prices[pet]}")

            return await ctx.send(embed=embed)
        except Exception:
            traceback.print_exc()

    @commands.command(name="rename")
    async def rename_(self, ctx, *, pet):
        """Rename a pet"""
        account = await self.manager.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To create one please use `p-create`")
        
        if not account.pets:
            return await ctx.send("You do not have any pets to rename. To adopt one please use `p-adopt`")
        
        pet = RenameConverter.convert(ctx, pet)

        if not pet[0]:
            return await ctx.send(f"You do not own a pet named {pet}. To buy an animal use `p-adopt`")

        await self.bot.db.execute("UPDATE pets SET name = $1 WHERE owner_id = $2 AND name = $3", pet[1], ctx.author.id, pet[0].name)

    @commands.command(name="inspect")
    async def inspect_(self, ctx, *, pet):
        """Inspect a pet"""
        pet = pet.lower()
        account = await self.manager.get_account(ctx.author.id)

        try:
            if not account:
                return await ctx.send("You do not have an account. To create one please use `p-create`")
            
            if not account.pets:
                return await ctx.send("You do not have any pets to inspect. To adopt one please use `p-adopt`")
            
            pets = account.pets
            if pet not in [p.name.lower() for p in pets]:
                return await ctx.send(f"You do not own a pet named {pet}. To buy an animal use `p-adopt`")

            pet = await self.manager.get_pet_named(ctx.author.id, pet)

            embed = discord.Embed(title=f"Inspecting {pet.name}", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            
            for key, value in vars(pet).items():
                key = key.replace("_"," ")
                if key.lower() not in  ["earns", "species"]:
                    embed.add_field(name=f"{str(key)[0].upper()}{str(key)[1:]}", value=f"{str(value)[0].upper()}{str(value)[1:]}")
                elif key.lower() == "earns":
                    value = value*pet.level*self.bot.pet_species[pet.type][pet.species][1]/pet.level*2
                    embed.add_field(name=f"{str(key)[0].upper()}{str(key)[1:]}", value=f"${str(value)[0].upper()}{str(value)[1:]}")
                else:
                    value = f"{self.bot.pet_species[pet.type][value][0]} {value} {pet.type}"
                    embed.add_field(name="Species", value=f"{value[0].upper()}{value[1:]}")
            
            return await ctx.send(embed=embed)
        except Exception:
            traceback.print_exc()

    @commands.command(name="feed")
    async def feed_(self, ctx, item, *, pet):
        """Feed a pet a certain amount of food"""
        pet = pet.lower()
        account = await self.manager.get_account(ctx.author.id)

        try:
            if not account:
                return await ctx.send("You do not have an account. To create one please use `p-create`")

            if not account.pets:
                return await ctx.send("You do not have any pets to feed. To adopt one please use `p-adopt`")

            pets = account.pets
            if pet not in [p.name.lower() for p in pets]:
                return await ctx.send(f"You do not own a pet named {pet}. To buy an animal use `p-adopt`")

            pet = await self.manager.get_pet_named(ctx.author.id, pet)
            items = account.items

            pet_type = pet.type

            try:
                food = items[item]
            except KeyError:
                return await ctx.send(f"It looks like you do not have any {item}.")

            shop = self.bot.shop
            shop_cog = self.bot.cogs["ShopManager"]

            if item not in shop_cog.valid_items.keys():
                return await ctx.send("That item does not exist.")

            if pet.hunger < 10:
                gain = shop[item]["gain"]
                pet_hunger = pet.hunger + gain

                if pet_hunger > 10:
                    pet_hunger = 10

                await ctx.send(
                    f"Your pet has gained {gain} hunger. It's health bar has changed to {pet_hunger}/10")

                if (food - 1) <= 0:
                    del items[item]
                else:
                    items[item] = items[item] - 1

                await self.bot.db.execute("UPDATE accounts SET items = $1 WHERE owner_id = $2", json.dumps(items), ctx.author.id)

                return await self.bot.db.execute("UPDATE pets SET hunger = $1 WHERE owner_id = $2 AND name = $3",
                                                 pet_hunger, ctx.author.id, pet.name)
            else:
                return await ctx.send(f"{pet.name} is on full hunger. You can check all of your pets' hunger and thirst "
                                      f"bars using `p-pets`")
        except Exception:
            traceback.print_exc()

    @commands.command(name="water")
    async def water_(self, ctx, *, pet):
        """Give a pet a certain amount of water. Default amount is 1"""
        pet = pet.lower()
        account = await self.manager.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To create one please use `p-create`")

        if not account.pets:
            return await ctx.send("You do not have any pets to feed. To adopt one please use `p-adopt`")

        pets = account.pets
        if pet not in [p.name.lower() for p in pets]:
            return await ctx.send(f"You do not own a pet named {pet}. To buy an animal use `p-adopt`")

        pet = await self.manager.get_pet_named(ctx.author.id, pet)
        items = account.items

        if "water bowls" in items.keys():
            water = items["water bowls"]
        else:
            return await ctx.send(f"It looks like you do not have any water. Please buy some using the `p-buy` command")

        if water <= 0:
            return await ctx.send(f"It looks like you do not have any water. Please buy some using the `p-buy` command")

        try:
            pet_thirst = pet.thirst
            amount_needed = 20 - pet_thirst

            if pet_thirst < 3:
                pet_thirst = pet.thirst + amount_needed

                await ctx.send(
                    f"Your pet has gained {str(amount_needed)[:4]} thirst. It's thirst bar has changed to {str(pet_thirst)[:4]}/20")
            else:
                amount = random.uniform(1.0, amount_needed)
                pet_thirst = pet.thirst + amount

                if pet_thirst > 20:
                    pet_thirst = 20

                await ctx.send(
                    f"Your pet has gained {str(amount)[:4]} thirst. It's thirst bar has changed to {str(pet_thirst)[:4]}/20")

            items["water bowls"] = items["water bowls"] - 1

            await self.bot.db.execute("UPDATE accounts SET items = $1 WHERE owner_id = $2", json.dumps(items), ctx.author.id)

            return await self.bot.db.execute("UPDATE pets SET thirst = $1 WHERE owner_id = $2 AND name = $3",
                                                pet_thirst, ctx.author.id, pet.name)
                                        

        except KeyError:
            return await ctx.send(f"Your {pet} is on full thirst. You can check all of your pets' hunger and thirst "
                                  f"bars using `p-pets`")


def setup(bot):
    bot.add_cog(Pets(bot))
