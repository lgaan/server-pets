from discord.ext import commands

class NotVoted(commands.CommandError):
    pass

def has_voted():
    async def pred(ctx):
        if not await ctx.bot.has_voted(ctx.author):
            raise NotVoted("You haven't voted")
            return False
        else:
            return True
    
    return commands.check(pred)