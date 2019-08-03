import traceback
import json
import asyncio

import discord
from discord.ext import commands

from helpers.paginator import EmbedPaginator

class Shopping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_items_food = {
            "dog food": 35,
            "cat food": 20,
            "mouse food": 10,
            "snake food": 50,
            "spider food": 45,
            "bird food": 30,
            "horse food": 60
        }
        self.shop_items_water = {
            "water": 5,
            "one bowl": 5,
            "two bowls": 10,
            "three bowls": 15,
            "four bowls": 18,
            "five bowls": 20,
            "six bowls": 22,
            "seven bowls": 25,
        }
        self.conversions = {
            "water": 1,
            "one bowl": 1,
            "two bowls": 2,
            "three bowls": 3,
            "four bowls": 4,
            "five bowls": 5,
            "six bowls": 6,
            "seven bowls": 7,
        }

    @commands.command(name="shop", aliases=["buy"])
    async def shop_(self, ctx, *, item=None):
        """Displays the shop is item is left empty. You can buy an item by adding it to the command."""
        account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)
        amount = 1
        if item is None:
            embed_food = discord.Embed(title=f"{ctx.guild}'s food shop", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            embed_water = discord.Embed(title=f"{ctx.guild}'s water shop", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

            for key, value in self.shop_items_food.items():
                embed_food.add_field(name=key, value=f"${value}")

            for key, value in self.shop_items_water.items():
                embed_water.add_field(name=key, value=f"${value}")
            
            if account:
                embed_food.add_field(name="-"*56, value="** **", inline=False)
                embed_food.add_field(name="Current Balance", value=f"${account[0]['balance']}", inline=False)

                embed_water.add_field(name="-"*56, value="** **", inline=False)
                embed_water.add_field(name="Current Balance", value=f"${account[0]['balance']}", inline=False)

            embed_food.set_thumbnail(url=ctx.guild.icon_url)
            embed_water.set_thumbnail(url=ctx.guild.icon_url)

            return await ctx.paginate(message=None, entries=[embed_food, embed_water])
        
        try:
            if not account:
                return await ctx.send("You do not have an account. Please make one using `p-create`")
            
            if (item not in self.shop_items_food.keys()) and (item not in self.shop_items_water.keys()):
                return await ctx.send("That item does not exist. Please check the options from `p-shop` and make sure to type the capitals correctly.")

            is_water = (item not in self.shop_items_food.keys())

            if is_water:
                if account[0]["balance"] < (self.shop_items_water[item]*amount):
                    return await ctx.send(f"This item costs ${self.shop_items_water[item]*amount}, you do not have enough cash to buy this item. Please wait until you have more cash.")

                confirm_embed = discord.Embed(title="Confirm Order", description="Use the up and down arrows to change the amount of items you wish to order.\nPlease react with <:greenTick:596576670815879169> to confirm the order, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                confirm_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

                confirm_embed.add_field(name="Amount of Items", value=amount)
                confirm_embed.add_field(name="Cost", value=f"${amount*self.shop_items_water[item]}")
                bot_msg = await ctx.send(embed=confirm_embed)

                await bot_msg.add_reaction("\u2b06")
                await bot_msg.add_reaction("\u2b07")
                await bot_msg.add_reaction(":greenTick:596576670815879169")
                await bot_msg.add_reaction(":redTick:596576672149667840")

                changing = True
                while changing:
                    try:
                        reaction, _ = await self.bot.wait_for("reaction_add", timeout=600, check=lambda r, u: u == ctx.author and str(r.emoji) in ["\u2b06","\u2b07","<:greenTick:596576670815879169>", "<:redTick:596576672149667840>"])
                        if str(reaction.emoji) == "\u2b06":
                            amount += 1
                            new_embed = discord.Embed(title="Confirm Order", description="Use the up and down arrows to change the amount of items you wish to order.\nPlease react with <:greenTick:596576670815879169> to confirm the order, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                            new_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

                            new_embed.add_field(name="Amount of Items", value=amount)
                            new_embed.add_field(name="Cost", value=f"${amount*self.shop_items_water[item]}")
                            await bot_msg.edit(embed=new_embed)
                        if str(reaction.emoji) == "\u2b07":
                            if (amount - 1) <= 0:
                                amount = 1
                            else:
                                amount -= 1
                            new_embed = discord.Embed(title="Confirm Order", description="Use the up and down arrows to change the amount of items you wish to order.\nPlease react with <:greenTick:596576670815879169> to confirm the order, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                            new_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

                            new_embed.add_field(name="Amount of Items", value=amount)
                            new_embed.add_field(name="Cost", value=f"${amount*self.shop_items_water[item]}")
                            await bot_msg.edit(embed=new_embed)
                        if str(reaction.emoji) == "<:greenTick:596576670815879169>":
                            changing = False
                        if str(reaction.emoji) == "<:redTick:596576672149667840>":
                            await bot_msg.delete()
                            changing = True

                            return await ctx.send("Canceled.")
                    except asyncio.TimeoutError:
                        await bot_msg.delete()
                        return await ctx.send("Canceled.")

                balance = (account[0]["balance"] - (self.shop_items_water[item]*amount))

                try:
                    amount_of_bowls = json.loads(account[0]["items"])["water bowls"] + (self.conversions[item]*amount)
                except KeyError:
                    amount_of_bowls = (self.conversions[item]*amount)
            else:
                if account[0]["balance"] < (self.shop_items_food[item]*amount):
                    return await ctx.send(f"This item costs ${self.shop_items_food[item]*amount}, you do not have enough cash to buy this item. Please wait until you have more cash.")

                confirm_embed = discord.Embed(title="Confirm Order", description="Use the up and down arrows to change the amount of items you wish to order.\nPlease react with <:greenTick:596576670815879169> to confirm the order, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                confirm_embed.set_thumbnail(url=ctx.guild.me.avatar_url)
                confirm_embed.add_field(name="Amount of Items", value=amount)
                confirm_embed.add_field(name="Cost", value=f"${amount*self.shop_items_food[item]}")
                bot_msg = await ctx.send(embed=confirm_embed)

                await bot_msg.add_reaction("\u2b06")
                await bot_msg.add_reaction("\u2b07")
                await bot_msg.add_reaction(":greenTick:596576670815879169")
                await bot_msg.add_reaction(":redTick:596576672149667840")

                changing = True
                while changing:
                    try:
                        reaction, _ = await self.bot.wait_for("reaction_add", timeout=600, check=lambda r, u: u == ctx.author and str(r.emoji) in ["\u2b06","\u2b07","<:greenTick:596576670815879169>", "<:redTick:596576672149667840>"])
                        if str(reaction.emoji) == "\u2b06":
                            amount += 1
                            new_embed = discord.Embed(title="Confirm Order", description="Use the up and down arrows to change the amount of items you wish to order.\nPlease react with <:greenTick:596576670815879169> to confirm the order, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                            new_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

                            new_embed.add_field(name="Amount of Items", value=amount)
                            new_embed.add_field(name="Cost", value=f"${amount*self.shop_items_food[item]}")
                            await bot_msg.edit(embed=new_embed)
                        if str(reaction.emoji) == "\u2b07":
                            if (amount - 1) <= 0:
                                amount = 1
                            else:
                                amount -= 1
                            new_embed = discord.Embed(title="Confirm Order", description="Use the up and down arrows to change the amount of items you wish to order.\nPlease react with <:greenTick:596576670815879169> to confirm the order, or <:redTick:596576672149667840> to cancel.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
                            new_embed.set_thumbnail(url=ctx.guild.me.avatar_url)

                            new_embed.add_field(name="Amount of Items", value=amount)
                            new_embed.add_field(name="Cost", value=f"${amount*self.shop_items_food[item]}")
                            await bot_msg.edit(embed=new_embed)
                        if str(reaction.emoji) == "<:greenTick:596576670815879169>":
                            changing = False
                        if str(reaction.emoji) == "<:redTick:596576672149667840>":
                            await bot_msg.delete()
                            changing = True

                            return await ctx.send("Canceled.")
                    except asyncio.TimeoutError:
                        await bot_msg.delete()
                        return await ctx.send("Canceled.")

                balance = (account[0]["balance"] - (self.shop_items_food[item]*amount))

            await bot_msg.delete()
            data = json.loads(account[0]["items"])
            
            if not is_water:
                try:
                    data[item] = data[item] + amount
                except KeyError:
                    data[item] = amount
            else:
                data["water bowls"] = amount_of_bowls

            await self.bot.db.execute("UPDATE accounts SET items = $1, balance = $2 WHERE owner_id = $3", json.dumps(data), balance, ctx.author.id)

            if item in self.shop_items_food.keys():
                desc = f"You bought {amount} bags of {item} for ${amount*self.shop_items_food[item]}"
            else:
                desc = f"You bought {amount*self.conversions[item]} bowl(s) of water for ${amount*self.shop_items_water[item]}"

            embed = discord.Embed(title="Success!", description=desc, colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
            embed.add_field(name="Old balance", value=f"${account[0]['balance']}")
            if item in self.shop_items_food.keys():
                embed.add_field(name="New balance", value=f"${account[0]['balance']-(self.shop_items_food[item]*amount)}")
            else:
                embed.add_field(name="New balance", value=f"${account[0]['balance']-(self.shop_items_water[item]*amount)}")

            return await ctx.send(embed=embed)
        except Exception as error:
            traceback.print_exc()

            return await ctx.send("Something went wrong and your account has not been charged.")

def setup(bot):
    bot.add_cog(Shopping(bot))