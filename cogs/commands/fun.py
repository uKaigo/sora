from io import BytesIO
from bs4 import BeautifulSoup
from random import choice
from re import sub
from discord import File
from discord.ext import commands
from ksoftapi import NoResults
from utils.custom import Embed

class Fun(commands.Cog, name='_fun_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(attach_files=True)
    async def meme(self, ctx):
        sv = 'br.' if ctx.lang == 'pt-br' else ''

        async with ctx.typing():
            res = await self.bot.session.get(f'https://{sv}ifunny.co/feeds/shuffle')

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
                
                url = f'https://{sv}ifunny.co'+list(list(choosen.children)[1].children)[0].attrs['href']
                url = sub('\?gallery\=[\w\d]+', '', url)

                to_send = await self.bot.session.get(choosen.attrs['data-source'])
                io = BytesIO(await to_send.read())
                await ctx.send(f'Link: <{url}>', file=File(io, filename=f'meme.{ext}'))
            else: # É uma imagem
                url = f'https://{sv}ifunny.co'+list(list(choosen.children)[1].children)[1].attrs['href']
                url = sub('\?gallery\=[\w\d]+', '', url)

                _surl = list(list(list(choosen.children)[1].children)[1].children)[0].attrs['data-src']
                to_send = await self.bot.session.get(_surl)
                io = BytesIO(await to_send.read())
                await ctx.send(f'Link: <{url}>', file=File(io, filename=f'meme.jpg'))

    @commands.command()
    async def reddit(self, ctx, subreddit):
        await ctx.trigger_typing()
        nsfw = ctx.channel.is_nsfw()

        try:
            image = await self.bot.apis.ksoft.images.random_reddit(
                subreddit,
                remove_nsfw=not nsfw # Para inverter o valor
            )
        except NoResults:
            nsfw_message = '.'
            if not nsfw:
                nsfw_message = '. Talvez por que você está usando o comando fora de um canal nsfw.'
            return await ctx.send('Nenhuma imagem encontrada' + nsfw_message)

        embed = Embed(ctx, description=image.title)
        embed.set_author(name=f'{image.author.strip("/")} em {image.subreddit}', url=image.source)
        embed.set_image(url=image.image_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))