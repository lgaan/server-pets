from datetime import datetime

import discord
from discord.ext import commands, tasks

from utils.managers.kennelmanager import KennelManager as km
from utils.managers.accountmanager import AccountManager

class KennelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kennels = km(bot)
        self.accounts = AccountManager(bot)

        self.managment.start()

    @tasks.loop(hours=24)
    async def managment(self):
        kennels = await self.kennels.get_active_kennels()

        if kennels:
            for kennel in kennels:
                account = await self.accounts.get_account(kennel.owner_id)
                if datetime.utcnow().strftime(r"%Y/%m/%d") == kennel.release_date.strftime(r"%Y/%m/%d"):
                    if not kennel.overdue:
                        await self.bot.get_user(kennel.owner_id).send(f"Your pet {kennel.name} has completed its time in the kennel, to collect them use `p-kennel collect`. (You will be charged $75 for every day you go over)")
                        await self.bot.db.execute("UPDATE kennel SET overdue = True WHERE owner_id = $1 AND name = $2", kennel.owner_id, kennel.name)
                    else:
                        await self.bot.get_user(kennel.owner_id).send(f"Your pet has not been collected, as a result your account has been charged $75. To collect your pet use `p-kennel`")
                        await self.kennels.charge_account(account, 75)

                continue

    @managment.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(KennelManager(bot))
