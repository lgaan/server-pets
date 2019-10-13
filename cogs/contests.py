import discord
from discord.ext import commands

import traceback
import string
import random

from utils.converters import MultiStringConverter
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
                a_id = random.randint(1000000000,15000000000)
                json = {
                    "owner_id": a_id,
                    "balance": random.randint(1000, 10000),
                    "items": {"water bowls": random.randint(0, 20), "steak": random.randint(0, 5)},
                    "settings": {"dm_notifications": True, "death_reminder": True},
                    "pets": [Pet({"owner_id": a_id, "name": random.choice(["Dave", "Joe", "Susan", "Cherry"]), "type": random.choice(["dog", "cat", "mouse", "bird", "horse", "snake", "spider"]), "hunger": random.randint(10, 20), "thirst": random.randint(10, 20), "level": random.randint(1, 5)}) for x in range(random.randint(1, 3))]
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

        if not contests:
            embed = discord.Embed(title="Contests", colour=discord.Colour.blue(), description="You are not in any contests. To view a list use `p-contests` and to join one use `p-contest join <id>`", timestamp=ctx.message.created_at)

            return await ctx.send(embed=embed)

        entries = []
        for l in self.bot.chunk(contests, 5):
            embed = discord.Embed(title="Your Contests", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

            for contest in l:
                embed.add_field(name=contest.id, value=f"Entry Fee: {contest.fee} | Reward: {contest.reward} | Status: {contest.status}", inline=False)

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
                    if contest.status != "playing":
                        embed.add_field(name=contest.id, value=f"Entry Fee: ${contest.fee} | Reward: ${contest.reward} | Status: {contest.status}", inline=False)

                embed.set_thumbnail(url=ctx.me.avatar_url)

                entries.append(embed)
            
            return await ctx.paginate(message=None, entries=entries)
    
    @commands.group(name="contest")
    async def contest_(self, ctx):
        """Group command, create, join and leave contests"""
        return
    
    @contest_.command(name="info")
    async def info_(self, ctx, contest_id: int):
        """See a contest's status"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contest = await self.manager.get_contest(contest_id)

        if not contest:
            return await ctx.send("This contest does not exist, or is private. To see a list of contests use `p-contests`.")

        embed = discord.Embed(title=f"Contest {contest_id}", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
        embed.add_field(name="Status", value=f"{contest.status[0].upper()}{contest.status[1:]}", inline=False)
        embed.add_field(name="Npcs", value=len(contest.npcs) if contest.npcs else "None")
        embed.add_field(name="Users", value=len(contest.participants))

        embed.add_field(name="** **", value="** **", inline=False)
        embed.add_field(name="Entry Cost", value=f"${contest.fee}", inline=False)
        embed.add_field(name="Prize", value=f"${contest.reward}", inline=False)

        return await ctx.send(embed=embed)

    @contest_.command(name="create", aliases=["add"])
    async def create_(self, ctx, name: MultiStringConverter, entry_fee: int, prize: int):
        """Create a contest, this costs $500 to do"""
        try:
            name = " ".join(name)
            if entry_fee >= prize:
                return await ctx.send("You cant have the entry fee greater than or equal to the reward.")

            account = await self.accounts.get_account(ctx.author.id)

            if not account:
                return await ctx.send("You do not have an account. To make one use `p-create`")
            
            message = await ctx.send("Would you like npcs in your contest? Reply with `yes` or `no`.")

            id = random.randint(1000000, 10000000)
            try:
                reply = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author == ctx.author)

                if reply.content.lower() in ["yes", "y"]:
                    npcs = await self.generate_npcs(random.randint(1, 10))

                    json = {
                        "owner_id": ctx.author.id,
                        "id": id,
                        "name": name,
                        "npcs": [acc.to_json() for acc in npcs],
                        "users": [account.to_json()],
                        "fee": entry_fee,
                        "reward": prize,
                        "status": "idle"
                    }
                    contest = await self.manager.create_contest(json)

                elif reply.content.lower() in ["no", "n"]:
                    json = {
                        "owner_id": ctx.author.id,
                        "id": id,
                        "name": name,
                        "users": [account.to_json()],
                        "fee": entry_fee,
                        "reward": prize,
                        "status": "idle"
                    }

                    contest = await self.manager.create_contest(json)
                else:
                    return await ctx.send("Cancelled.")
            
            except TimeoutError:
                return await ctx.send("Time ran out.")

            if account.balance < 500:
                return await ctx.send("You do not have enough money to start a contest.")

            await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account.balance-500, ctx.author.id)

            return await ctx.send(f"Contest created! You can view your contest using `p-contest info {id}` (This has cost you $500)")
        except Exception:
            traceback.print_exc()

    @contest_.command(name="start")
    async def start_(self, ctx, contest_id: int):
        """Start a contest"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contest = await self.manager.get_contest(contest_id)

        if not contest:
            return await ctx.send("This contest does not exist, or is private. To see a list of contests use `p-contests`.")
        
        if contest.owner_id != ctx.author.id:
            return await ctx.send("You do not own this contest.")
        
        if len(contest.participants) == 1 and not contest.npcs:
            return await ctx.send("This contest has only you in it. Wait for others to join.")

        await self.bot.db.execute("UPDATE contests SET status = $1 WHERE owner_id = $2 AND id = $3", "playing", ctx.author.id, contest_id)

        return await ctx.send("Contest started! Just sit back, and wait for the results.")

    @contest_.command(name="delete")
    async def delete_(self, ctx, contest_id: int):
        """Delete a contest"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contest = await self.manager.get_contest(contest_id)

        if not contest:
            return await ctx.send("This contest does not exist, or is private. To see a list of contests use `p-contests`.")
        
        if contest.owner_id != ctx.author.id:
            return await ctx.send("You do not own this contest.")
        
        await self.manager.delete_contest(contest_id, ctx.author.id)

        return await ctx.send("Contest deleted.")

    @contest_.command(name="join")
    async def join_(self, ctx, contest_id: int):
        """Join a contest"""
        account = await self.accounts.get_account(ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To make one use `p-create`")
        
        contest = await self.manager.get_contest(contest_id)

        if not contest:
            return await ctx.send("This contest does not exist, or is private. To see a list of contests use `p-contests`.")
        
        if account.balance < contest.fee:
            return await ctx.send("You dont have enough money to enter this contest.")
        
        await ctx.send(f"This will cost you ${contest.fee}, would you like to continue? Reply with `yes` to continue, or anything else to cancel.")

        try:
            message = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author.id == ctx.author.id)

            if message.content.lower() not in ["yes", "y"]:
                return await ctx.send("Cancelled.")
        except TimeoutError:
            return await ctx.send("Time ran out.")

        users = contest.participants

        if not account.to_json()["owner_id"] in [u["owner_id"] for u in users]:
            users.append(account.to_json())

            await self.bot.db.execute("UPDATE contests SET users = $1 WHERE id = $2", users, contest_id)
            await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account.balance - contest.fee, account.id)

            return await ctx.send(f"You have joined the contest `{contest_id}`, I will notify you when it starts.")
        else:
            return await ctx.send("You are already in this contest.")

def setup(bot):
    bot.add_cog(Contests(bot))