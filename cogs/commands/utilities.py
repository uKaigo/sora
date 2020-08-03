import re
from asyncio import TimeoutError
from typing import Union
from json import load
from os import getenv
from datetime import datetime
from io import BytesIO
import pyfiglet
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from ffz import Client, NotFound
from utils.custom import baseMenu, Embed

class Utils(commands.Cog, name='_utils_cog'):
    def __init__(self, bot):
        self.bot = bot
        self.ffz = bot.apis.ffz = Client(loop=bot.loop, session=bot.session)

    @commands.command(name='ascii')
    async def _ascii(self, ctx, fonte, *, texto):
        await ctx.trigger_typing()

        try:
            fnt = pyfiglet.Figlet(font=fonte)
        except pyfiglet.FontNotFound:
            embed = Embed(ctx, title=ctx.t('err_invalid'), description=ctx.t('invalid_desc'), error=True)
            return await ctx.send(embed=embed)

        txt = fnt.renderText(texto)

        if len(txt) > 2000-6:
            io = BytesIO(txt.encode())
            args = dict(content=f'Online:\n...\nDownload:', file=discord.File(io, 'ascii.txt'))

        else:
            args = dict(content=f'```{txt}```')

        m = await ctx.send(**args)
        if 'file' in args:
            url = f'https://txt.discord.website/?txt={m.attachments[0].url[38:-4].strip("/")}'
            await m.edit(content=f'Online:\n<{url}>\nDownload:')

    @commands.group(aliases=['qr'], invoke_without_command=True, case_insensitive=True)
    async def qrcode(self, ctx, *, texto):
        if ctx.invoked_subcommand is None:
            texto = texto.replace(' ', '%20')
            embed = Embed(ctx, title=ctx.t('title'), color=self.bot.neutral)
            embed.set_image(url=f'http://api.qrserver.com/v1/create-qr-code/?data={texto}&size=500x500')

            await ctx.send(embed=embed)

    @qrcode.command()
    async def read(self, ctx, *, url=None):
        nofile = Embed(ctx, title=ctx.t('err_nofile'), description=ctx.t('nofile_desc'), error=True)

        if not url:
            try:
                url = ctx.message.attachments[0].url
            except:
                return await ctx.send(embed=nofile)

        async with ctx.typing():
            response = await self.bot.session.get(f'http://api.qrserver.com/v1/read-qr-code/?fileurl={url}')

            try:
                async with response:
                    response = await response.json()
                    response = response[0]
            except Exception as e:
                return await ctx.send(embed=nofile)

            if response['symbol'][0]['error']:
                embed = Embed(ctx, title=ctx.t('err_invalid'), error=True)
                embed.description = ctx.t('invalid_desc')
                return await ctx.send(embed=embed)

        embed = Embed(ctx, title=ctx.t('title'), color=self.bot.neutral)
        embed.add_field(name=ctx.t('exit'), value=response['symbol'][0]['data'], inline=False)
        embed.add_field(name=ctx.t('type'), value=response['type'])
        await ctx.send(embed=embed)

    @commands.command()
    async def barcode(self, ctx, *, texto):
        barcode = await self.bot.session.get(f'http://bwipjs-api.metafloor.com/?bcid=code128&text={texto}')

        text = str()
        try:
            text = await barcode.text()
        except:
            pass
    
        if text.startswith('Error:'):
            embed = Embed(ctx, description=ctx.t('error'), error=True)
            return await ctx.send(embed=embed)
        
        embed = Embed(ctx, title=ctx.t('title'))
        embed.set_image(url=barcode.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['mcbody'])
    async def skin(self, ctx, nick):
        nick = nick[:200]
        embed = Embed(ctx)
        embed.description = f'[{ctx.t("download")}](https://minecraft.tools/download-skin/{nick}) | [{ctx.t("model")}](https://mc-heads.net/body/{nick})'
        embed.set_author(name=ctx.t('emb_title', nick=nick), icon_url=f'https://minotar.net/helm/{nick}/300.png')
        embed.set_image(url=f'https://mc-heads.net/body/{nick}')
        embed.set_thumbnail(url=f'https://minecraftskinstealer.com/api/v1/skin/render/fullbody/{nick}/700')
        await ctx.send(embed=embed)

    @commands.command(aliases=['git'])
    async def github(self, ctx, usuario):
        base_url=f'https://api.github.com/users/{usuario}'
        user = await self.bot.session.get(base_url)

        if user.status != 200:
            erro = Embed(ctx, error=True)
            erro.description = ctx.t(f'err_{user.status}')
           
            if user.status == 404:
                erro.title = ctx.t('err_404')
                erro.description = ctx.t('notfound_desc')
    
            return await ctx.send(embed=erro)
        
        user = await user.json()

        embed = Embed(ctx)
        embed.description = user.get('bio', discord.Embed.Empty)

        nome = user['name'] if user['name'] else user['login']
        embed.set_author(name=ctx.t('emb_title', name=nome), icon_url=user['avatar_url'], url=user['html_url'])

        embed.add_field(name=ctx.t('emb_uname'), value=user['login'], inline=False)
        embed.add_field(name=ctx.t('load_repo'), value=ctx.t('loading'), inline=False)
        embed.add_field(name=ctx.t('emb_follow'), value=ctx.t('follow_desc', followers=user['followers'], following=user['following']), inline=False)

        if user['email']:
            embed.add_field(name=ctx.t('emb_email'), value=ctx.t('email'))

        created = datetime.strptime(user['created_at'], '%Y-%m-%dT%H:%M:%SZ')

        embed.set_footer(text=f'Conta criada em:', icon_url=ctx.author.avatar_url)
        embed.timestamp = created

        m = await ctx.send(embed=embed)

        embed.remove_field(1)
        repos = await self.bot.session.get(base_url + '/repos')
        repos = await repos.json()

        user_repos = [f'[{c["name"]}]({c["html_url"]}) ==={c["fork"]}'.replace('===True', '_forked_').replace('===False', '') for c in repos]
        if len(user_repos) > 15:
            user_repos = user_repos[:15]
            user_repos.append(ctx.t('more', repos=user['public_repos']-15))

        user_repos = [ctx.t('none')] if not user_repos else user_repos
        embed.insert_field_at(1, name=ctx.t('emb_repo', repos=user['public_repos']), value='\n'.join(user_repos), inline=False)
        await m.edit(embed=embed)

    @commands.command()
    async def addbot(self, ctx, member: Union[discord.Member, discord.Object], permissions='8'):
        _id = member.id

        if not str(_id).isdigit():
            embed = Embed(ctx, title=ctx.t('err_invalid'), description=ctx.t('not_member'), error=True)
            return await ctx.send(embed=embed)

        invalid = False

        if not permissions.isdigit():
            invalid = True
            permissions = '8'

        base_url = 'https://discordapp.com/oauth2/authorize?scope=bot&client_id={}&permissions={}'     

        if not isinstance(member, discord.Member):
            member = await self.bot.fetch_user(_id) 
        if not member.bot:
            embed = Embed(ctx, title=ctx.t('err_invalid'), description=ctx.t('invalid_desc'), error=True)
            return await ctx.send(embed=embed)

        embed = Embed(ctx, title=ctx.t('emb_title', name=member.name))
        embed.description = f'{base_url.format(member.id, permissions)}\n\n{ctx.t("perm_inv") if invalid else ""}'
        await ctx.send(embed=embed)

    @commands.command(name='ffz')
    async def _ffz(self, ctx, emote):
        async with ctx.typing():
            await self.ffz.wait_until_ready()
            try:
                em = await self.ffz.search_emote(emote, limit=1)
            except NotFound:
                embed = Embed(ctx, title=ctx.t('err_notfound'), error=True)
                embed.description = ctx.t('notfound_desc')
                return await ctx.send(embed=embed)
        embed = Embed(ctx, title=ctx.t('emb_title', name=em.name))
        embed.description = ctx.t(
            'emb_desc', 
            creator_name=em.owner.display_name,
            creator_twitch=em.owner.twitch_url,
            usage=em.usage,
            emote_link=em.url)
        embed.set_image(url=f'https:{em.image}')
        m = await ctx.send(embed=embed)

        if not ctx.me.permissions_in(ctx.channel).manage_emojis \
                or not ctx.author.permissions_in(ctx.channel).manage_emojis:
            return

        await m.add_reaction('➕')
        
        def check(r, user):
            return user == ctx.author and r.message.id == m.id and r.emoji == '➕'
        try:
            # Não preciso acessar oq retorna, já que eu ja sei (pelo check)       
            await self.bot.wait_for('reaction_add', check=check, timeout=60)
        except TimeoutError:
            return await m.remove_reaction('➕', ctx.me)

        async with ctx.typing():
            img = await self.bot.session.get(f'https:{em.image}')
            img_bytes = await img.read()
            io = BytesIO(img_bytes)
            try:
                emoji = await ctx.guild.create_custom_emoji(
                    name=em.name, 
                    image=io.read(), 
                    reason=str({ctx.author})
                )
            except discord.HTTPException as error:
                if error.status == 400:
                    return await ctx.send(ctx.t('emote_limit'))
                raise error
        await ctx.send(ctx.t('emote_add', emote=emoji, emote_name=em.name))

    @commands.command()
    async def report(self, ctx, member:discord.Member, *, msg):
        async def invalid_report():
            await self.bot.db.guilds.update({'_id': ctx.guild.id, 'report': None})
            return await ctx.send(ctx.t('err_nset'))

        _guild = await self.bot.db.guilds.find(ctx.guild.id)
        
        channel = ctx.guild.get_channel(_guild["report"])

        if not _guild.get('report'):
            return await ctx.send(ctx.t('err_nset'))

        if not channel:
            await invalid_report()

        _rep = Embed(ctx, title=ctx.t('rep_title'))
        _rep.description = ctx.t('rep_desc', author_mention=ctx.author.mention, member_mention=member.mention, reason=msg)
        
        try:
            await channel.send(embed=_rep)
        except discord.Forbidden:
            await invalid_report()

        await ctx.send(ctx.t('success'))
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Utils(bot))