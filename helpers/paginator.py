import traceback
import asyncio

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
        self.page += 1

        try:
            await self.message.edit(embed=self.entries[self.page])
        except IndexError:
            return
    
    async def page_backward(self):
        self.page -= 1

        try:
            await self.message.edit(embed=self.entries[self.page])
        except IndexError:
            return
    
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