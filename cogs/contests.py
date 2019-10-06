import discord
from discord.ext import commands

import traceback
import string
import random

from utils.managers.contestmanager import ContestManager
from utils.managers.accountmanager import AccountManager
from utils.objects.account import Account
from utils.objects.pet import Pet

class Contests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.manager = ContestManager(bot)
        self.accounts = AccountManager(bot)
    
    async def generate_npcs(self, amount):
        """Generate an amount of nps"""
        try:
            npcs = []
            for incr in range(amount):
                id = int(''.join([str(random.choice(range(0, 10))) for x in range(18)]))
                json = {
                    "id": id,
                    "balance": random.randint(1000, 10000),
                    "items": {"water bowls": random.randint(0, 20), "steak": random.randint(0, 5)},
                    "settings": {"dm_notifications": True, "death_reminder": True},
                    "pets": [Pet({"owner_id": id, "name": random.choice(["Dave", "Joe", "Susan", "Cherry"]), "type": random.choice(["dog", "cat", "mouse", "bird", "horse", "snake", "spider"]), "hunger": random.randint(10, 20), "thirst": random.randint(10, 20), "level": random.randint(1, 5)}) for x in range(random.randint(1, 3))]
                }

                npcs.append(Account(json))
            
            return npcs
        except Exception:
            traceback.print_exc()

    @commands.command(name="my-contests")
    async def my_contests_(self, ctx):
        """Get a list of your contests"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contests = await self.manager.get_account_contests(ctx.author.id)

        entries = []
        for l in self.bot.chunk(contests, 5):
            embed = discord.Embed(title="Your Contests", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

            for contest in l:
                embed.add_field(name=contest.id, value=f"Entry Fee: {contest.fee} | Reward: {contest.reward}", inline=False)

            embed.set_thumbnail(url=ctx.author.avatar_url)

            entries.append(embed)
        
        return await ctx.paginate(message=None, entries=entries)

    @commands.command(name="contests")
    async def contests_(self, ctx):
        """Get a list of global contests"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contests = await self.manager.get_contests()

        if not contests:
            embed = discord.Embed(title="Contests", colour=discord.Colour.blue(), description="There are no running contests. Use `p-contest create` to create one.", timestamp=ctx.message.created_at)

            return await ctx.send(embed=embed)
        else:
            entries = []
            for l in self.bot.chunk(contests, 5):
                embed = discord.Embed(name="Global Contests", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

                for contest in l:
                    embed.add_field(name=contest.id, value=f"Entry Fee: ${contest.fee} | Reward: ${contest.reward}")

                embed.set_thumbnail(url=ctx.me.avatar_url)

                entries.append(embed)
            
            return await ctx.paginate(message=None, entries=entries)
    
    @commands.group(name="contest")
    async def contest_(self, ctx):
        """Group command, create, join and leave contests"""
        return
    
    @contest_.command(name="create", aliases=["add"])
    async def create_(self, ctx, name, entry_fee: int, prize: int):
        """Create a contest, this costs $500 to do"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        message = await ctx.send("Would you like this to be a global contest? If you reply with `no`, you will be against NPCS; if you reply with `yes` other players can join until you run `p-contest start <id>`.")

        try:
            reply = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author == ctx.author)

            if reply.content == "no":
                npcs = await self.generate_npcs(random.randint(1, 10))

                json = {
                    "owner": ctx.author.id,
                    "id": int(''.join([str(random.randint(0,9)) for x in range(10)])),
                    "name": name,
                    "npcs": [acc.to_json() for acc in npcs],
                    "users": [account.to_json()],
                    "fee": entry_fee,
                    "reward": prize
                }
                contest = await self.manager.create_contest(json)

            elif reply == "yes":
                json = {
                    "owner": ctx.author.id,
                    "id": int(''.join([str(random.randint(0,9)) for x in range(10)])),
                    "name": name,
                    "users": [account.to_json()],
                    "fee": entry_fee,
                    "reward": prize
                }

                contest = await self.manager.create_contest(json)
            else:
                return await ctx.send("Cancelled.")
        
        except TimeoutError:
            return await ctx.send("Time ran out.")

        return await ctx.send(contest)

    @contest_.command(name="join")
    async def join_(self, ctx, contest_id: int):
        """Join a contest"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contest = await self.manager.get_contest(contest_id)

        if not contest:
            return await ctx.send("This contest does not exist, or is private. To see a list of contests use `p-contests`.")
        
        users = contest.participants

        if not account.to_json()["owner_id"] in [u["owner_id"] for u in users]:
            users.append(account.to_json())

            await self.bot.db.execute("UPDATE constests SET users = $1 WHERE id = $2", users, contest_id)

            return await ctx.send("You have joined the contest `{contest_id}`, I will notify you when it starts.")
        else:
            return await ctx.send("You are already in this contest.")

def setup(bot):
    bot.add_cog(Contests(bot))