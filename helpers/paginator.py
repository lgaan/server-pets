import asyncio

import discord

class Paginator:
    def __init__(self, ctx, entries: list, embed=True):
        self.bot = ctx.bot
        self.ctx = ctx
        self.entries = entries
        self.embed = embed
        self.max_pages = len(entries)-1
        self.msg = ctx.message
        self.paginating = True
        self.user_ = ctx.author
        self.channel = ctx.channel
        self.current = 0
        self.reactions = [('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.first_page),
                          ('\N{BLACK LEFT-POINTING TRIANGLE}', self.backward),
                          ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.forward),
                          ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.last_page),
                          ('\N{INPUT SYMBOL FOR NUMBERS}', self.selector),
                          ('\N{BLACK SQUARE FOR STOP}', self.stop),
                          ('\N{INFORMATION SOURCE}', self.info)]

    async def setup(self):
        if self.embed is False:
            try:
                self.msg = await self.channel.send(self.entries[0])
            except AttributeError:
                await self.channel.send(self.entries)
        else:
            try:
                self.msg = await self.channel.send(embed=self.entries[0])
            except (AttributeError, TypeError):
                await self.channel.send(embed=self.entries)

        if len(self.entries) == 1:
            return

        for (r, _) in self.reactions:
            await self.msg.add_reaction(r)

    async def alter(self, page: int):
        try:
            await self.msg.edit(embed=self.entries[page])
        except (AttributeError, TypeError):
            await self.msg.edit(content=self.entries[page])

    async def first_page(self):
        self.current = 0
        await self.alter(self.current)

    async def backward(self):
        if self.current == 0:
            self.current = self.max_pages
            await self.alter(self.current)
        else:
            self.current -= 1
            await self.alter(self.current)

    async def forward(self):
        if self.current == self.max_pages:
            self.current = 0
            await self.alter(self.current)
        else:
            self.current += 1
            await self.alter(self.current)

    async def last_page(self):
        self.current = self.max_pages
        await self.alter(self.current)

    async def selector(self):
        def check(m):
            if m.author == self.user_:
                return True
            if m.message == self.msg:
                return True
            if int(m.content) > 1 <= self.max_pages+1:
                return True
            return False

        delete = await self.channel.send(f"Which page do you want to turn to? **1-{self.max_pages+1}?**")
        try:
            number = int((await self.bot.wait_for('message', check=check, timeout=60)).content)
        except asyncio.TimeoutError:
            return await self.ctx.send("You ran out of time.")
        else:
            self.current = number - 1
            await self.alter(self.current)
            await delete.delete()

    async def stop(self):
        try:
            await self.msg.clear_reactions()
        except discord.Forbidden:
            await self.msg.delete()

        self.paginating = False

    async def info(self):
        embed = discord.Embed(color=discord.Colour.blue())
        embed.set_author(name='Instructions')
        embed.description = "This is a reaction paginator; when you react to one of the buttons below " \
                            "the message gets edited. Below you will find what the reactions do."

        embed.add_field(name="First Page ⏮", value="This reaction takes you to the first page.", inline=False)
        embed.add_field(name="Previous Page ◀", value="This reaction takes you to the previous page. "
                                                      "If you use this reaction while in the first page it will take"
                                                      "you to the last page.", inline=False)
        embed.add_field(name="Next Page ▶", value="This reaction takes you to the next page. "
                                                  "If you use this reaction while in the last page it will to take"
                                                  "you to the first page.", inline=False)
        embed.add_field(name="Last Page ⏭", value="This reaction takes you to the last page", inline=False)
        embed.add_field(name="Selector 🔢", value="This reaction allows you to choose what page to go to", inline=False)
        embed.add_field(name="Information ℹ", value="This reaction takes you to this page.")
        await self.msg.edit(embed=embed)

    def _check(self, reaction, user):
        if user.id != self.user_.id:
            return False

        if reaction.message.id != self.msg.id:
            return False

        for (emoji, func) in self.reactions:
            if reaction.emoji == emoji:
                self.execute = func
                return True
        return False

    async def paginate(self):
        perms = self.ctx.me.guild_permissions.manage_messages
        await self.setup()
        while self.paginating:
            if perms:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=self._check, timeout=120)
                except asyncio.TimeoutError:
                    return await self.stop()

                try:
                    await self.msg.remove_reaction(reaction, user)
                except discord.HTTPException:
                    pass

                await self.execute()
            else:
                done, pending = await asyncio.wait(
                    [self.bot.wait_for('reaction_add', check=self._check, timeout=120),
                     self.bot.wait_for('reaction_remove', check=self._check, timeout=120)],
                    return_when=asyncio.FIRST_COMPLETED)
                try:
                    done.pop().result()
                except asyncio.TimeoutError:
                    return self.stop

                for future in pending:
                    future.cancel()
                await self.execute()