import traceback

import re
import shlex

import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands

from utils.managers.accountmanager import AccountManager

DATE_REGEX = r"(?i)^(\d+)(d(ays|ay)?|w(eeks|eek)?|m(onths|onth)?|y(ears|ear)?)$"
DAY_REGEX = r"^(3[01]|[12][0-9]|[1-9])$"
WEEK_REGEX = r"^([1-4])$"
MONTH_REGEX = r"^([1-9]|[1][0-2])$"

class CommandOrCog(commands.Converter):
    async def convert(self, ctx, argument):
        cog_conversions = {cog.lower(): cog for cog in ctx.bot.cogs}
        try:
            return ctx.bot.get_cog(cog_conversions[argument.lower()]) if argument.lower() in cog_conversions.keys() else ctx.bot.get_command(argument.lower())
        except Exception as error:
            traceback.print_exc()
            raise commands.BadArgument(error)

class KennelDate(commands.Converter):
    async def convert(self, ctx, argument):
        match = re.match(DATE_REGEX, argument)

        if not match:
            raise commands.BadArgument("Amount of time is not in the correct form. Use `<number><d/w/m/y>`")

        match = match.groups()

        if not re.match(DAY_REGEX, match[0]) and match[1].lower() in ["d","days","day"]:
            raise commands.BadArgument("Amount of days is too low or too high, consider using `m`, or `w`.")
        
        if not re.match(WEEK_REGEX, match[0]) and match[1].lower() in ["w","weeks","week"]:
            raise commands.BadArgument("Amount of weeks is too low or too high, consider using `m`, or `y`.")
        
        if not re.match(MONTH_REGEX, match[0]) and match[1].lower() in ["m","months","month"]:
            raise commands.BadArgument("Amount of months is too low or too high, consider using `y`.")

        now = datetime.utcnow()

        if match[1].lower() in ["d","days","day"]:
            d = now + timedelta(days=int(match[0]))
        
        if match[1].lower() in ["w","weeks","week"]:
            d = now + timedelta(weeks=int(match[0]))
        
        if match[1].lower() in ["m","months","month"]:
            d = now + relativedelta(months=+int(match[0]))
        
        if match[1].lower() in ["y","years","year"]:
            d = now + relativedelta(years=+int(match[0]))

        return d

class RenameConverter(commands.Converter):
    async def convert(self, ctx, argument):
        manager = AccountManager(ctx.bot)
        has_quotes = any(word.startswith('"') or word.startswith("'") for word in argument.split(" "))

        if has_quotes and not argument.split(" ")[0].startswith("'") and not argument.split(" ")[0].startswith('"'):
            raise commands.BadArgument("If using quotes, they must be on the first argument, e.g. `p-rename \"pet\" new name`")
        
        pet = await manager.get_pet_named(ctx.author.id, shlex.split(argument)[0] if has_quotes else argument.split(" ")[0])

        return (pet, ' '.join(argument.split(" ")[1:]))