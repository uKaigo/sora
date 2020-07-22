from os import getenv
from asyncio import TimeoutError
from utils.custom import baseMenu, Embed
from discord.ext import commands

class LyricsMenu(baseMenu):
    def __init__(self, pages, song, msg_obj):
        self._obj = msg_obj
        self._song = song
        self._title = f'{song.artist} - {song.name}'
        super().__init__(pages, self._title, '')
    
    async def send_initial_message(self, ctx, channel):
        await self._obj.edit(content='', embed=self.embed)
        return self._obj

    @property 
    def embed(self):
        msg = self.pages[self._index].strip()
        msg += '...' if not self._index == len(self.pages)-1 and self.should_add_reactions() else ''
        embed = Embed(self.ctx, description=msg)
        embed.set_footer(text='Ksoft.Si')
        embed.set_author(name=self._title, icon_url=self._song.album_art)
        return embed

class Music(commands.Cog, name='_music_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['letra', 'l'])
    async def lyrics(self, ctx, *, query):
        _results = await self.bot.apis.ksoft.music.lyrics(query)
        if not _results:
            embed = Embed(ctx, title=ctx.t('err_notfound'), error=True)
            embed.description = ctx.t('notfound_desc')
            return await ctx.send(embed=embed)

        op = [f'- **{i}**: {s.artist} - {s.name}' for i, s in enumerate(_results, 1)]

        embed = Embed(
            ctx, 
            title='Sora | Lyrics', 
            description=ctx.t('opts_desc') + '\n\n' + '\n'.join(op)
        )

        embed.set_footer(text=ctx.t('opts_footer'))

        msg = await ctx.send(embed=embed)

        def check(m):
            return (m.channel, ctx.author) == (ctx.channel, ctx.author) \
                and (bool(m.content), m.content.isdecimal()) == (True, True) \
                and 0 < int(m.content) <= len(_results) or m.content.lower() == 'exit'
        
        try:
            res = await self.bot.wait_for('message', check=check, timeout=60)
        except TimeoutError:
            res = None
        
        if not res or res.content.lower() == 'exit':
            return await msg.delete()
        
        song = _results[int(res.content) - 1] 
        lyrics = song.lyrics

        pages = self.bot.paginator(lyrics, 2045)

        menu = LyricsMenu(pages, song, msg)
        await menu.start(ctx)

def setup(bot):
    bot.add_cog(Music(bot))