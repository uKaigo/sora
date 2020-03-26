import discord
from genius import Client
from os import getenv
from assets.models.menus import baseMenu
from asyncio import TimeoutError
from discord.ext import commands


class Music(commands.Cog, name='_music_cog'):
    def __init__(self, bot):
        self.bot = bot
        self.genius = Client(getenv('genius_token'))

    @commands.command(aliases=['lyrics', 'l'])
    async def letra(self, ctx, *, query):
        trn = await ctx.trn
        _results = await self.genius.search(query)
        if not _results:
            embed = await self.bot.erEmbed(ctx, trn['err_notfound'])
            embed.description = trn['notfound_desc']
            return await ctx.send(embed=embed)

        op = [f'- **{i}**: [{s.artist} - {s}]({s.url})' for i, s in enumerate(_results, 1)]

        embed = await self.bot.embed(ctx)
        embed.title = 'Sora | Lyrics'
        embed.description = trn['opts_desc'] + '\n\n' + '\n'.join(op)
        embed.set_footer(text=trn['opts_footer'].format(author_name=ctx.author.name), icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content \
                and m.content.isdecimal() and 0 < int(m.content) <= len(_results) or m.content.lower() == 'exit'
        
        try:
            res = await self.bot.wait_for('message', check=check, timeout=60)
        except TimeoutError:
            res = None
        
        if not res or res.content.lower() == 'exit':
            return await msg.delete()
        
        song = _results[int(res.content) - 1]
        lyrics = await self.genius.get_lyrics(song)
        if not lyrics:
            embed = await self.bot.erEmbed(ctx, trn['err_nolyric'])
            embed.description = trn['nolyric_desc']
        
        pages = self.bot.paginator(lyrics, 2045)

        menu = baseMenu(pages, f'{song.artist} - {song}', '', '...', msg_obj=msg)
        await menu.start(ctx)

def setup(bot):
    bot.add_cog(Music(bot))