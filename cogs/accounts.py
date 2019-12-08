import traceback
import asyncio
import json

import discord
from discord.ext import commands

from utils.managers.accountmanager import AccountManager

class Accounts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = AccountManager(bot)

        self.conversion = {
            "dog food": "Dog Food",
            "cat food": "Cat Food",
            "mouse food": "Mouse Food",
            "snake food": "Snake Food",
            "spider food": "Spider Food",
            "bird food": "Bird Food",
            "horse food": "Horse Food",
            "water bowls": "Water Bowls"
        }
        
        self.badges = {
            "badget1p": "<:badget1p:652944771744268349>",
            "badget2p": "<:badget2p:652944772159242251>",
            "badgeadmin": "<:badgeadmin:653200112163618847>"
        }

    @commands.command(name="create")
    async def create_(self, ctx):
        """Creates an account"""
        account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)

        if account:
            return await ctx.send("You already have an account! To view it please say `p-account`.")

        await self.manager.create_account(ctx.author.id)

        return await ctx.message.add_reaction(":greenTick:596576670815879169")

    @commands.command(name="delete")
    async def delete_(self, ctx):
        """Deletes an account"""
        account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account!")

        confirm_embed = discord.Embed(title="Confirm",
                                      description="Are you sure?\nPlease react with <:greenTick:596576670815879169> to confirm, or <:redTick:596576672149667840> to cancel.",
                                      colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
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
                return await ctx.send("Canceled.")
        except asyncio.TimeoutError:
            return await ctx.send("Time ran out.")

        await self.bot.db.execute("DELETE FROM accounts WHERE owner_id = $1", ctx.author.id)
        await self.bot.db.execute("DELETE FROM pets WHERE owner_id = $1", ctx.author.id)

        return await ctx.send("Your account has been deleted.")

    @commands.command(name="account", aliases=["profile"])
    async def account_(self, ctx, user: discord.Member = None):
        """Get the account of a user or yourself."""
        try:
            user = ctx.author if user is None else user
            account = await self.manager.get_account(user.id)

            if not account:
                return await ctx.send("The user in question does not have an account. Use `p-create` to make one.")

            embed = discord.Embed(title=f"{user.name}'s account. ({user.id})", colour=discord.Colour.blue(),
                                  timestamp=ctx.message.created_at)
            embed.set_thumbnail(url=user.avatar_url)

            if not account.pets:
                embed.add_field(name="Pets", value="None")
            else:
                sorted_pets = await account.sort_pets()

                v = []
                for key, value in sorted_pets.items():
                    if key == "mouse" and value > 1:
                        v.append(f"{value} {key}")
                    else:
                        v.append(f"{value} {key}(s)")

                embed.add_field(name="Pets", value=', '.join(v))

            if account.pets:
                embed.add_field(name="Currently earning", value=f"${sum((p.earns*p.level*self.bot.pet_species[p.type][p.species][1]/p.level*2) for p in account.pets)}/30 minutes")
            embed.add_field(name="Balance", value=f"${account.balance}")

            if account.badges:
                string = []
                for badge in account.badges:
                    emote = self.badges[badge]
                    
                    string.append(emote)
                    
                embed.add_field(name="Badges", value=', '.join(string))
            return await ctx.send(embed=embed)
        except Exception:
            traceback.print_exc()

    @commands.command(name="pets")
    async def pets_(self, ctx, user: discord.Member = None):
        """Find out the hunger and thirst of a users or your animals."""
        try:
            user = ctx.author if user is None else user

            account = await self.manager.get_account(user.id)

            if not account:
                return await ctx.send("The user in question does not have an account.")

            if not account.pets:
                embed = discord.Embed(title=f"{user.name}'s animals.", colour=discord.Colour.blue(),
                                  timestamp=ctx.message.created_at)
                embed.add_field(name="This user has no pets.", value="** **")

                return await ctx.send(embed=embed)
            else:
                print("yaya")
                entries = []
                for l in self.bot.chunk(account.pets, 5):
                    embed = discord.Embed(title=f"{user.name}'s animals.", colour=discord.Colour.blue(),
                                  timestamp=ctx.message.created_at)
                    for pet in l:
                        val = ""

                        # hunger
                        try:
                            val += f"Hunger: {str(pet.hunger)[:4]}/20"
                        except KeyError:
                            val += f"Hunger: 10/10"

                        # thirst
                        try:
                            val += f"\nThirst: {str(pet.thirst)[:4]}/20"
                        except KeyError:
                            val += f"\nThirst: 20/20"

                        embed.add_field(name=f"{pet.name.upper()[0]}{pet.name[1:]} (Level {pet.level} {pet.type}), {pet.age[0].upper()}{pet.age[1:]} {'| Kenneled' if pet.kenneled else ''}", value=val, inline=False)

                    embed.set_thumbnail(url=user.avatar_url)

                    entries.append(embed)
                
                return await ctx.paginate(message=None, entries=entries)
        except Exception:
            traceback.print_exc()

    @commands.command(name="supplies", aliases=["inventory", "inv"])
    async def supplies_(self, ctx, user: discord.Member = None):
        """Shows the supplies of a user or yourself."""
        try:
            user = ctx.author if user is None else user
            account = await self.manager.get_account(user.id)

            if not account:
                return await ctx.send("The user in question does not have an account.")

            items = account.items

            embed = discord.Embed(title=f"{user.name}'s supplies", colour=discord.Colour.blue(),
                                  timestamp=ctx.message.created_at)

            for key, value in items.items():
                if key != "water bowls":
                    embed.add_field(name=f"{key[0].upper()}{key[1:]}", value=value, inline=False)

            embed.add_field(name="Water Bowls", value=items["water bowls"], inline=False)

            embed.set_thumbnail(url=user.avatar_url)
            return await ctx.send(embed=embed)
        except Exception:
            traceback.print_exc()

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard_(self, ctx, lb_type=None):
        """Get a leaderboard of the people in your server or globally. For server leave `lb_type` empty, for global use `p-lb global`"""
        try:
            accounts, unchunked = await self.manager.get_lb_accounts(ctx, lb_type if lb_type is not None else "server")

            print(unchunked)
            entries = []
            
            for l in accounts:
                embed = discord.Embed(title="Global leaderboard" if lb_type else f"{ctx.guild}'s leaderboard", colour=discord.Colour.blue())
                
                for account in l:
                    index = unchunked.index(account.id) + 1

                    user = self.bot.get_user(account.id)

                    embed.add_field(name=f"{index} | {user}",
                                    value=f"{len(account.pets) if account.pets else '0'} pets, has ${account.balance}",
                                    inline=False)
                    embed.add_field(name="** **", value="** **", inline=False)

                embed.set_thumbnail(url=ctx.guild.me.avatar_url if lb_type else ctx.guild.icon_url)
                embed.set_footer(text=f"Your rank: {unchunked.index(ctx.author.id) + 1}", icon_url=ctx.author.avatar_url)
                entries.append(embed)

            return await ctx.paginate(message=None, entries=entries)
        except Exception:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Accounts(bot))
