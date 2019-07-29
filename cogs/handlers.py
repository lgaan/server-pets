import discord
from discord.ext import commands

class Handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

        await ctx.author.send(f"An error occured in your command! If you are unable to fix this please join the support server to get help.\n**Error: {error}**")
        return await ctx.message.add_reaction(":cdnbroke:596577460573831169")

def setup(bot):
    bot.add_cog(Handlers(bot))