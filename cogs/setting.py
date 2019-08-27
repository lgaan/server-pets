import traceback
import json

import discord
from discord.ext import commands

from utils.paginator import SettingsPaginator
class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.conversions = {
            True: "<:greenTick:596576670815879169>",
            False: "<:redTick:596576672149667840>",
            **dict.fromkeys(["dm_notifications","dm notifictions","dms","dm"], "dm_notifications")
        }
    
    @commands.command(name="settings")
    async def settings_(self, ctx):
        """A command for showing the bot settings for your account, or changing them."""
        account = await self.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", ctx.author.id)

        if not account:
            return await ctx.send("You do not have an account. To create one use `p-create`")

        account_settings = json.loads(account[0]["settings"])

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

def setup(bot):
    bot.add_cog(Settings(bot))
