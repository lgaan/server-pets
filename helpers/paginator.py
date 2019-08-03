import traceback
import asyncio
import json

import discord

class EmbedPaginator:
    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.message = kwargs.get("message")
        self.entries = kwargs.get("entries")

        self.looping = True
        self.page = 0
        self.last_page = 0
    
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }
    
    async def react(self):
        for emote in self.emotes.keys():
            await self.message.add_reaction(emote)

    async def page_forward(self):
        try:
            await self.message.edit(embed=self.entries[self.page+1])
        except IndexError:
            return

        self.page += 1
    
    async def page_backward(self):
        try:
            await self.message.edit(embed=self.entries[self.page-1])
        except IndexError:
            return
        
        self.page -= 1
    
    async def stop(self):
        return await self.message.delete()

    async def paginate(self):
        self.message = await self.ctx.send(embed=self.entries[self.page]) if self.message is None else self.message

        await self.react()

        while self.looping:
            try:
                try:
                    reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=30.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in ["\u2b05","\u27a1","\u23f9"])

                    if str(reaction.emoji) != "\u23f9":
                        await self.emotes[str(reaction.emoji)]()
                    else:
                        self.looping = False
                except asyncio.TimeoutError:
                    self.looping = False
            except Exception:
                traceback.print_exc()
        
        return await self.stop()
    
class SettingsPaginator:
    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.message = kwargs.get("message")
        self.entries = kwargs.get("entries")

        self.conversions = {
            True: "<:greenTick:596576670815879169>",
            False: "<:redTick:596576672149667840>"
        }

        self.looping = True
        self.setting = 0
        self.last_page = 0
    
        self.emotes = {
            "\u2b05": self.last_setting,
            "\u27a1": self.next_setting,
            "\U0001f504": self.switch_setting,
            "\u23f9": self.stop
        }
    
    async def react(self):
        for emote in self.emotes.keys():
            await self.message.add_reaction(emote)

    async def next_setting(self):
        try:
            if (self.setting + 1) >= len(self.entries):
                return

            embed = discord.Embed(title=f"{self.ctx.author.name}'s settings", colour=discord.Colour.blue(), timestamp=self.ctx.message.created_at)

            fields = [f.name for f in self.message.embeds[0].fields]

            for field in self.message.embeds[0].fields:
                if fields.index(field.name) == (self.setting + 1):
                    # Highlighted
                    embed.add_field(name=f"> {fields[fields.index(field.name)]}", value=field.value)
                else:
                    # Not highlighted
                    embed.add_field(name=field.name.replace("> ",""), value=field.value)

            await self.message.edit(embed=embed)
        except IndexError:
            return
        
        self.setting += 1
    
    async def last_setting(self):
        try:
            if (self.setting - 1) < 0:
                return

            embed = discord.Embed(title=f"{self.ctx.author.name}'s settings", colour=discord.Colour.blue(), timestamp=self.ctx.message.created_at)

            incr = 0
            fields = [f.name for f in self.message.embeds[0].fields]

            for field in self.message.embeds[0].fields:
                if fields.index(field.name) == (self.setting - 1):
                    # Highlighted
                    embed.add_field(name=f"> {fields[fields.index(field.name)]}", value=field.value)
                else:
                    # Not highlighted
                    embed.add_field(name=field.name.replace("> ",""), value=field.value)

            await self.message.edit(embed=embed)
        except IndexError:
            return
        
        self.setting -= 1
    
    async def switch_setting(self):
        account = await self.ctx.bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", self.ctx.author.id)

        field = self.message.embeds[0].fields[self.setting]
        setting = field.name.replace("> ","").replace(field.name.replace("> ","")[0],field.name.replace("> ","")[0].lower()).replace(" ","_")

        settings = json.loads(account[0]["settings"])
        settings[setting] = not settings[setting]

        embed = discord.Embed(title=f"{self.ctx.author.name}'s settings", colour=discord.Colour.blue(), timestamp=self.ctx.message.created_at)

        incr = 0
        for field in self.message.embeds[0].fields:
            if incr == self.setting:
                embed.add_field(name=field.name, value=self.conversions[settings[setting]])
            else:
                embed.add_field(name=field.name, value=field.value)

            incr += 1

        await self.ctx.bot.db.execute("UPDATE accounts SET settings = $1 WHERE owner_id = $2", json.dumps(settings), self.ctx.author.id)
        
        return await self.message.edit(embed=embed)

    async def stop(self):
        return await self.message.delete()

    async def paginate(self):
        self.message = await self.ctx.send(embed=self.entries[self.page]) if self.message is None else self.message

        await self.react()

        while self.looping:
            try:
                try:
                    reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=30.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in ["\u2b05","\u27a1","\u23f9","\U0001f504"])

                    if str(reaction.emoji) != "\u23f9":
                        await self.emotes[str(reaction.emoji)]()
                    else:
                        self.looping = False
                except asyncio.TimeoutError:
                    self.looping = False
            except Exception:
                traceback.print_exc()
        
        return await self.stop()