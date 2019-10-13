import discord
from discord.ext import commands, tasks

import traceback
import random
import numpy as np

from utils.managers.contestmanager import ContestManager as ContManager
from utils.managers.accountmanager import AccountManager
from utils.objects.account import Account

class ContestManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = ContManager(bot)
        self.accounts = AccountManager(bot)

        self.looper.start()

        self.chances = None
    
    async def register_winner(self, contest, winner_tuple: tuple):
        """Register a contest winner"""
        winner = "npc" if winner_tuple[0].startswith("npc") else str(self.bot.get_user(winner_tuple[2]))

        await self.bot.db.execute("UPDATE contests SET winner = $1 WHERE owner_id = $2 AND id = $3", winner, contest.owner_id, contest.id)

        if winner != "npc":
            await self.bot.get_user(winner_tuple[2]).send(f"You won contest {contest.id}! You have earnt ${contest.reward}")

            account = await self.accounts.get_account(winner_tuple[2])

            await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", account.balance + contest.reward, winner_tuple[2])
        
        return winner

    @tasks.loop(hours=2)
    async def looper(self):
        """Manage the contests"""
        try:
            contests = await self.manager.get_contests()

            if not contests:
                return

            for contest in contests:
                if contest.status == "idle":
                    # Contest hasnt been started
                    continue
                
                await self.bot.db.execute("UPDATE contests SET round_num = $1 WHERE id = $2", contest.round_num + 1, contest.id)

                if contest.npcs:
                    accounts = [*[Account(u, type="user") for u in contest.participants], *[Account(npc, type="npc") for npc in contest.npcs]]
                else:
                    accounts = [Account(u, type="user") for u in contest.participants]

                if contest.winner or len(accounts) == 0:
                    await self.manager.delete_contest(contest.id, contest.owner_id)

                    owner = self.bot.get_user(contest.owner_id)

                    try:
                        await owner.send(f"Contest {contest.id} has finished after {contest.round_num-1} round(s), the winner {'was an npc' if contest.winner == 'npc' else f'was {contest.winner}'}")
                    except discord.Forbidden:
                        return
                    
                    continue

                chance = 1
                chances = []

                for i, account in enumerate(accounts):
                    npcs = [a for a in accounts if a.type == "npc"]
                    users = [a for a in accounts if a.type == "user"]

                    if account.type == "npc":
                        # Account is an npc, we need to get a random chance of winning.
                        fl = random.uniform(chance, 1)

                        chance -= fl

                        c = random.uniform(0, fl)

                        chances.append((f"npc#{i}", c, account.id))
                    else:
                        # Account is a user
                        fl = random.uniform(chance, 1)
                        chance -= fl

                        c = random.uniform(0, fl)

                        chances.append((f"user#{i}", c, account.id))

                if len(chances) == 1:
                    winner_tuple = chances[0]

                    await self.register_winner(contest, winner_tuple)

                loosers = [entry for entry in chances if entry[1] < 0.5]

                if not contest.winner:
                    if not loosers:
                        a = random.choice(accounts)

                        loosers.append((f"{a.type}#1", 0.4, a.id))

                    for entry in loosers:
                        chances.remove(entry)

                        if len(loosers) == 1 and len(chances) == 0:
                            await self.register_winner(contest, entry)

                            break

                        if entry[1] < 0.5:
                            if entry[0].startswith("npc"):
                                npcs = {a.id: a for a in accounts if a.type == "npc"}

                                acc = npcs[entry[2]]

                                npcs = contest.npcs
                                npcs.remove(acc.to_json())

                                await self.bot.db.execute("UPDATE contests SET npcs = $1 WHERE id = $2", npcs, contest.id)

                            else:
                                users = {a.id: a for a in accounts if a.type == "user"}

                                acc = users[entry[2]]

                                users = contest.participants
                                users.remove(acc.to_json())

                                new_contest = await self.manager.get_contest(contest.id)

                                if new_contest.winner != str(self.bot.get_user(entry[2])):
                                    try:
                                        u = self.bot.get_user(entry[2])

                                        await u.send(f"You have lost in round {contest.round_num + 1} of contest {contest.id}! Better luck next time.")
                                    except discord.Forbidden:
                                        pass
                                    
                                    await self.bot.db.execute("UPDATE contests SET users = $1 WHERE id = $2", users, contest.id)
        except Exception:
            traceback.print_exc()

    @looper.before_loop
    async def before_loop(self):
        """Wait for bot ready"""
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(ContestManager(bot))