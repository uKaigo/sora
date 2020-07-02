from assets.packages import discordMenus as menus

__all__ = ('baseMenu',)

class baseMenu(menus.Menu):
    def __init__(self, pages, title, msg):
        super().__init__(clear_reactions_after=True, timeout=30)
        self.pages = [c for c in pages if c]
        if not pages:
            raise ValueError('Nenhuma página.')
        self._title = title
        self._msg = msg
        self._index = 0

    def should_add_reactions(self):
        if len(self.pages) == 1:
            return 0
        return len(self.buttons)
    
    async def send_initial_message(self, ctx, channel):
        return await ctx.send(embed=self.embed)

    @property 
    def embed(self):
        msg = self._msg
        msg += self.pages[self._index]
        embed = self.bot.embed(self.ctx)
        embed.title = self._title
        embed.description = msg 
        return embed

    @menus.button('◀️')
    async def back(self, _):
        self._index -= 1
        if self._index < 0:
            self._index = len(self.pages)-1
        return await self.message.edit(embed=self.embed)

    @menus.button('⏹')
    async def _stop(self, _):
        self.stop()

    @menus.button('▶️')
    async def foward(self, _):
        self._index += 1
        if self._index == len(self.pages):
            self._index = 0
        return await self.message.edit(embed=self.embed)
