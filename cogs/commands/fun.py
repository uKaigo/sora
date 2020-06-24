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
        embed = self.bot.embed(ctx, invisible=True)
        embed.description = ctx.t('loading')
        msg = await ctx.send(embed=embed)
        
        server = 'br.' if ctx.lang == 'pt-br' else ''

        res = await self.bot.session.get(f'https://{server}ifunny.co/page2')
        soup = BeautifulSoup(await res.text(), 'html.parser')
        
        to_choice = soup.find_all(class_='media__preview')
        to_choice = [a for a in to_choice if not a.attrs['href'].startswith('/video/')]
        to_choice = [c.find('img') for c in to_choice]

        if not to_choice:
            embed = self.bot.erEmbed(ctx, ctx.t('err_notfound'))
            embed.description = ctx.t('notfound_desc')
            return await msg.edit(embed=embed)

        meme = choice(to_choice)

        embed = self.bot.embed(ctx)
        embed.set_image(url=meme.attrs['data-src'])
        await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))