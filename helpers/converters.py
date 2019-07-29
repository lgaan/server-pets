import traceback

import discord
from discord.ext import commands

class CommandOrCog(commands.Converter):
    async def convert(self, ctx, argument):
        cog_conversions = {cog.lower(): cog for cog in ctx.bot.cogs}
        try:
            return ctx.bot.get_cog(cog_conversions[argument.lower()]) if argument.lower() in cog_conversions.keys() else ctx.bot.get_command(argument.lower())
        except Exception as error:
            traceback.print_exc()
            raise commands.BadArgument(error)