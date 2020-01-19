import traceback

import discord
from discord.ext import commands

from utils.paginator import SettingsPaginator
from utils.managers.accountmanager import AccountManager

from utils.checks import has_voted

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = AccountManager(bot)

        self.conversions = {
            True: "<:greenTick:596576670815879169>",
            False: "<:redTick:596576672149667840>",
            **dict.fromkeys(["dm_notifications","dm notifictions","dms","dm"], "dm_notifications")
        }
    
    @commands.command(name="settings")
    @has_voted()
    async def settings_(self, ctx):
        """A command for showing the bot settings for your account, or changing them."""
        try:
            account = await self.manager.get_account(ctx.author.id)

            if not account:
                return await ctx.send("You do not have an account. To create one use `p-create`")

            account_settings = account.settings

            embed = discord.Embed(title=f"{ctx.author.name}'s settings", description="Use the arrows to navigate between settings, use the switch emoji to change the setting.", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

            incr = 0
            for key, value in account_settings.items():
                val = f"{key[0].upper()}{key[1:]}".replace("_"," ")
                if incr == 0:
                    embed.add_field(name=f"> {val}", value=self.conversions[value])
                else:
                    embed.add_field(name=val, value=self.conversions[value])
                
                incr += 1

            msg = await ctx.send(embed=embed)
            return await SettingsPaginator(ctx=ctx, message=msg, entries=[key for key in account_settings.keys()]).paginate()
        except Exception:
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Settings(bot))
