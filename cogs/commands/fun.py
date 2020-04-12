import discord
from io import BytesIO
from random import choice
from bs4 import BeautifulSoup
from discord.ext import commands


class Fun(commands.Cog, name='_fun_cog'):
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
        
        to_choice = soup.find_all(class_='media__image')
        
        if not to_choice:
            embed = await self.bot.erEmbed(ctx, trn['err_notfound'])
            embed.description = trn['notfound_desc']
            return await msg.edit(embed=embed)

        meme = choice(to_choice)

        embed = await self.bot.embed(ctx)
        embed.description = meme.attrs['alt'].replace('\n', ' ')
        embed.set_image(url=meme.attrs['data-src'])
        await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))