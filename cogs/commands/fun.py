import discord
from io import BytesIO
from random import choice
from bs4 import BeautifulSoup
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        trn = await ctx.trn

        embed = await self.bot.embed(ctx, invisible=True)
        embed.description = trn['loading']
        msg = await ctx.send(embed=embed)
        
        server = {"pt-br": "br.", "en-us": ""}.get(await ctx.lang, "")
        
        res = await self.bot.session.get(f'https://{server}ifunny.co/page2')
        soup = BeautifulSoup(await res.text(), 'html.parser')
        
        imgs = soup.find_all(class_='media__image')
        videos = soup.find_all(class_='media__player')
        
        to_choice = imgs + videos
        
        if not to_choice:
            embed = await self.bot.erEmbed(ctx, trn['err_notfound'])
            embed.description = trn['notfound_desc']
            return await msg.edit(embed=embed)

        meme = choice(to_choice)

        meme_src = meme.attrs[{"img": "data-src", "video": "src"}[meme.name]]
        meme_type = {"img": "png", "video": "mp4"}[meme.name]

        _mres = await self.bot.session.get(meme_src)
        _io = BytesIO(await _mres.read())

        await msg.delete()
        await ctx.send(content=meme.attrs['alt'].replace('\n', ''), file=discord.File(fp=_io, filename=f'meme.{meme_type}'))

def setup(bot):
    bot.add_cog(Fun(bot))