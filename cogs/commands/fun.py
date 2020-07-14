from io import BytesIO
from bs4 import BeautifulSoup
from random import choice
from re import sub
from discord import File
from discord.ext import commands

class Fun(commands.Cog, name='_fun_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        server = 'br.' if ctx.lang == 'pt-br' else ''

        async with ctx.typing():
            res = await self.bot.session.get(f'https://{server}ifunny.co/')

            soup = BeautifulSoup(await res.text(), 'html.parser')
            
            to_choice = soup.find_all(class_='post__media')
            
            if not to_choice:
                embed = self.bot.erEmbed(ctx, ctx.t('err_notfound'))
                embed.description = ctx.t('notfound_desc')
                return await ctx.send(embed=embed)
            
            choosen = list(choice(to_choice).children)[1]

            # É um video/gif
            if choosen.attrs.get('data-type') and \
                    (ext := choosen.attrs['data-type']) in ['image', 'video']:
                ext = {'image': 'gif', 'video': 'mp4'}.get(ext) 
                
                url = 'https://ifunny.co'+list(list(choosen.children)[1].children)[0].attrs['href']
                url = sub('\?gallery\=[\w\d]+', '', url)

                to_send = await self.bot.session.get(choosen.attrs['data-source'])
                io = BytesIO(await to_send.read())
                await ctx.send(f'Link: <{url}>', file=File(io, filename=f'meme.{ext}'))
            else: # É uma imagem
                url = 'https://ifunny.co'+list(list(choosen.children)[1].children)[1].attrs['href']
                url = sub('\?gallery\=[\w\d]+', '', url)

                _surl = list(list(list(choosen.children)[1].children)[1].children)[0].attrs['data-src']
                to_send = await self.bot.session.get(_surl)
                io = BytesIO(await to_send.read())
                await ctx.send(f'Link: <{url}>', file=File(io, filename=f'meme.jpg'))

def setup(bot):
    bot.add_cog(Fun(bot))