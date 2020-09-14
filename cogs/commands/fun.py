from io import BytesIO
from bs4 import BeautifulSoup
from random import choice, randint
from re import compile as re_compile
from collections import namedtuple

from discord import File
from discord.ext import commands
from ksoftapi import APIError, NoResults
from pyfiglet import Figlet
from aiohttp import ClientConnectorError

from utils.custom import Embed

class NotFound(Exception): pass

class Fun(commands.Cog, name='_fun_cog'):
    def __init__(self, bot):
        self.bot = bot

    async def get_meme(self, soup: BeautifulSoup) -> namedtuple:
        """Retorna uma namedtuple contendo o post e a imagem do meme."""
        MemeTuple = namedtuple('Meme', 'post url')
        gallery_pattern = re_compile('\?gallery\=[\w\d]+')
        
        def get_href(element, is_image):
            num = 1 if is_image else 0
            return list(list(element.children)[1].children)[num].attrs['href']

        memes = soup.find_all(class_='post__media')
        if not memes:
            raise NotFound('Nenhum meme encontrado.')

        meme = list(choice(memes).children)[1]

        # image = gif, video = mp4
        if meme.attrs.get('data-type') in {'image', 'video'}:
            post = get_href(meme, False)
            url = meme.attrs['data-source']
        else:
            post = get_href(meme, True)
            # \/ Por algum motivo o jeito de pegar imagem no ifunny é HORRIVEL
            # então eu tenho que fazer isso.
            url = list(list(list(meme.children)[1].children)[1].children)[0].attrs['data-src']            

        post = gallery_pattern.sub('', post)

        return MemeTuple(post, url)

    @commands.command()
    @commands.bot_has_permissions(attach_files=True)
    async def meme(self, ctx):
        url = f'https://{"br." if ctx.lang == "pt-br" else ""}ifunny.co'
        url = url.strip('/')

        async with ctx.typing():
            request = await self.bot.session.get(f'{url}/feeds/shuffle')
            text = await request.text()

            try:
                meme = await self.get_meme(BeautifulSoup(text, 'html.parser'))
            except NotFound:
                embed = Embed(
                    ctx, 
                    title=ctx.t('err_notfound'), 
                    description=ctx.t('notfound_desc'), 
                    error=True
                )
                return await ctx.send(embed=embed)

            post_url = url + meme.post

            meme_ext = meme.url.split('.')[-1]
            meme_response = await self.bot.session.get(meme.url)
            meme_content = await meme_response.read()
            if len(meme_content) > int(7.99*1024*1024):
                return await ctx.reinvoke()

            meme_io = BytesIO(meme_content)

            attachment = File(meme_io, filename=f'meme.{meme_ext}')

            await ctx.send(f'Link: <{post_url}>', file=attachment)

    @commands.command()
    async def secret(self, ctx, number, *, text):
        await ctx.trigger_typing()
        if len(number) > 1 or not number.isdigit():
            return await ctx.send(ctx.t('err_invalid_n'))
        fnt = Figlet('banner3')
        txt = fnt.renderText(text)
        final = ''

        for c in txt:
            if c == ' ':
                n = randint(0, 9)
                while n == int(number):
                    n = randint(0, 9)
                final += str(n)
            else:
                final += c

        final = final.replace('#', number)

        if len(final) > 2000-9:
            if not ctx.me.permissions_in(ctx.channel).attach_files:
                return await ctx.send(ctx.t('err_too_big'))
            io = BytesIO(final.encode())
            args = dict(content=f'Online:\n...\nDownload:', file=File(io, 'secret.txt'))
        else:
            args = dict(content=f'```py\n{final}```')

        m = await ctx.send(**args)
        if 'file' in args:
            url = f'https://txt.discord.website/?txt={m.attachments[0].url[38:-4].strip("/")}'
            await m.edit(content=f'Online:\n<{url}>\nDownload:')


    @commands.command()
    async def reddit(self, ctx, subreddit):
        nsfw = ctx.channel.is_nsfw()

        async with ctx.typing():
            try:
                image = await self.bot.apis.ksoft.images.random_reddit(
                    subreddit,
                    remove_nsfw=not nsfw # Para inverter o valor.
                )
            except APIError as e:
                no_img = 'reddit returned no'
                no_sub = 'subreddit not found'

                message = ' '.join(e.message.split(' ')[:3])

                if not message in [no_img, no_sub]:
                    raise

                if message == no_sub:
                    return await ctx.send(ctx.t('err_notfound'))

                nsfw_message = ''
                if not nsfw:
                    nsfw_message = ' ' + ctx.t('maybe_nsfw')
                return await ctx.send(ctx.t('err_noimage') + nsfw_message)

            author = image.author.strip('/')
            sub = image.subreddit

            embed = Embed(ctx, description=image.title)

            embed.set_footer(text='Ksoft.Si')
            embed.set_author(name=ctx.t('title', author=author, sub=sub), url=image.source)
            embed.set_image(url=image.image_url)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))