import discord
import pyfiglet
import ffz
import re
from bs4 import BeautifulSoup
from json import load
from discord.ext import commands
from aiohttp import BasicAuth 
from os import getenv
from datetime import datetime
from assets.models.menus import baseMenu  

class Utils(commands.Cog, name='_utils_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ascii')
    async def _ascii(self, ctx, fonte, *, texto):
        trn = await ctx.trn
        embed = await self.bot.embed(ctx, invisible=True)
        embed.description = trn['loading']
        msg = await ctx.send(embed=embed)
        try:
            fnt = pyfiglet.Figlet(font=fonte)
        except pyfiglet.FontNotFound:
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            embed.description = trn["invalid_desc"]
            return await msg.edit(embed=embed)

        txt = fnt.renderText(texto)
        if len(txt) > 2000-10:
            embed = await self.bot.erEmbed(ctx, trn["err_big"])
            embed.description = trn["big_desc"]
            return await msg.edit(embed=embed)

        await msg.edit(embed=None, content=f'```{txt}```')       

    @commands.group(aliases=['qr'], invoke_without_command=True, case_insensitive=True)
    async def qrcode(self, ctx, *, texto):
        trn = await ctx.trn
        if ctx.invoked_subcommand is None:
            try:
                texto, cor = texto.split('#')
            except:
                cor = 'cccccc'

            embed = await self.bot.embed(ctx, invisible=True)
            embed.description = trn['loading']

            m = await ctx.send(embed=embed)
            
            qrcode = await self.bot.session.get(f'http://api.qrserver.com/v1/create-qr-code/?data={texto}&size=500x500&color={cor}&bgcolor=2F3136')
            
            embed = await self.bot.embed(ctx)
            embed.title = trn['title']
            embed.set_image(url=qrcode.url)

            await m.edit(embed=embed)

    @qrcode.command()
    async def read(self, ctx, *, url=None):
        trn = await ctx.trn
        nofile = await self.bot.erEmbed(ctx, trn["err_nofile"])
        nofile.description = trn["nofile_desc"]
        if not url:
            try:
                url = ctx.message.attachments[0].url
            except:
                return await ctx.send(embed=nofile)

        response = await self.bot.session.get(f'http://api.qrserver.com/v1/read-qr-code/?fileurl={url}')

        embed = await self.bot.embed(ctx, invisible=True)
        embed.description = trn["loading"]
        m = await ctx.send(embed=embed)
        try:
            async with response:
                response = await response.json()
                response = response[0]

        except:
            return await m.edit(embed=nofile)
        if response["symbol"][0]["error"]:
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            embed.description = trn["invalid_desc"]
            return await m.edit(embed=embed)

        embed = await self.bot.embed(ctx)
        embed.title = trn['title']
        embed.add_field(name=trn["exit"], value=response["symbol"][0]["data"], inline=False)
        embed.add_field(name=trn["type"], value=response["type"])
        await m.edit(embed=embed)

    @commands.command()
    async def barcode(self, ctx, *, texto):
        trn = await ctx.trn
        barcode = await self.bot.session.get(f'http://bwipjs-api.metafloor.com/?bcid=code128&text={texto}')

        text = str()
        try:
            text = await barcode.text()
        except:
            pass
    
        if text.startswith("Error:"):
            embed = await self.bot.erEmbed(ctx)
            embed.description = trn["error"]
            return await ctx.send(embed=embed)
        
        embed = await self.bot.embed(ctx)
        embed.title = trn["title"]
        embed.set_image(url=barcode.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['mcbody'])
    async def skin(self, ctx, nick):
        trn = await ctx.trn
        nick = nick[:200]
        embed = await self.bot.embed(ctx)
        embed.description = f'[{trn["download"]}](https://minecraft.tools/download-skin/{nick}) | [{trn["model"]}](https://mc-heads.net/body/{nick})'
        embed.set_author(name=trn["emb_title"].format(nick=nick), icon_url=f'https://minotar.net/helm/{nick}/300.png')
        embed.set_image(url=f'https://mc-heads.net/body/{nick}')
        embed.set_thumbnail(url=f'https://minecraftskinstealer.com/api/v1/skin/render/fullbody/{nick}/700')
        await ctx.send(embed=embed)

    @commands.command(aliases=['git'])
    async def github(self, ctx, usuario):
        trn = await ctx.trn
        base_url = f'https://api.github.com/users/{usuario}'
        git_name, git_token = getenv("git_token").split(":")
        auth = BasicAuth(git_name, git_token, 'utf-8')
        user = await self.bot.session.get(base_url, auth=auth)

        if user.status != 200:
            erro = await self.bot.erEmbed(ctx)
            erro.description = trn[f'err_{user.status}']
           
            if user.status == 404:
                erro.title = trn["err_404"]
                erro.description = trn["notfound_desc"]
    
            return await ctx.send(embed=erro)
        
        user = await user.json()

        embed = await self.bot.embed(ctx)
        embed.description = user.get("bio", discord.Embed.Empty)

        nome = user["name"] if user["name"] else user["login"]
        embed.set_author(name=trn["emb_title"].format(name=nome), icon_url=user["avatar_url"], url=user["html_url"])

        embed.add_field(name=trn["emb_uname"], value=user["login"], inline=False)
        embed.add_field(name=trn["load_repo"], value=trn['loading'], inline=False)
        embed.add_field(name=trn["emb_follow"], value=trn["follow_desc"].format(followers=user["followers"], following=user["following"]), inline=False)

        if user["email"]:
            embed.add_field(name=trn["emb_email"], value=user["email"])

        created = datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        created_tz = self.bot.utc_to_timezone(created, self.bot.timezone)
        with open(f'translation/{await ctx.lang}/commands.json', encoding='utf-8') as lng:
            time_lang = load(lng)["_time"]
        embed.add_field(name=trn["emb_created"], value=trn["created_desc"].format(created=created_tz.strftime("%d/%m/%Y %H:%M GMT-03"), 
        relative="".join(self.bot.getTime(time_lang, created)[0].replace(", ", "").replace("e ", ""))), 
        inline=False)

        m = await ctx.send(embed=embed)

        embed.remove_field(1)
        repos = await self.bot.session.get(base_url + '/repos', auth=auth)
        repos = await repos.json()

        user_repos = [f'[{c["name"]}]({c["html_url"]}) ==={c["fork"]}'.replace("===True", "_forked_").replace('===False', '') for c in repos]
        if len(user_repos) > 15:
            user_repos = user_repos[:15]
            user_repos.append(trn["more"].format(repos=user["public_repos"]-15))

        user_repos = [trn["none"]] if not user_repos else user_repos
        embed.insert_field_at(1, name=trn["emb_repo"].format(repos=user["public_repos"]), value='\n'.join(user_repos), inline=False)
        await m.edit(embed=embed)

    @commands.command()
    async def addbot(self, ctx, id, permissions='8'):
        trn = await ctx.trn
        invalid = False
        if not permissions.isdigit():
            invalid = True
            permissions = '8'
        base_url = 'https://discordapp.com/oauth2/authorize?scope=bot&client_id={}&permissions={}'     
        user = await self.bot.fetch_user(id) 
        if not user.bot:
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            embed.description = trn["invalid_desc"]
            return await ctx.send(embed=embed)  
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"].format(name=user.name)
        embed.description = f'{base_url.format(user.id, permissions)}\n\n{trn["perm_inv"] if invalid else ""}'
        await ctx.send(embed=embed)

    @commands.command(name='ffz')
    async def _ffz(self, ctx, emote):
        trn = await ctx.trn
        loading = await self.bot.embed(ctx, True)
        loading.description = trn['loading']
        m = await ctx.send(embed=loading)
        em = await ffz.search(emote)
        if not em:
            embed = await self.bot.erEmbed(ctx, trn['err_notfound'])
            embed.description = trn['notfound_desc']
            embed.description += trn['notfound_ath'] if '.' in emote else ''
            return await m.edit(embed=embed)
        embed = await self.bot.embed(ctx)
        embed.title = trn['emb_title'].format(name=em.name)
        embed.description = trn['emb_desc'].format(creator_name=em.creator.name, creator_twitch=em.creator.twitch, usage=em.usage, emote_link=em.url)
        embed.set_image(url=em.image)
        await m.edit(embed=embed)

    @commands.command(aliases=['corona', 'covid19', 'covid'])
    async def ncov(self, ctx):
        trn = await ctx.trn
        if True: #Imprementação futura
            res = await self.bot.session.get('https://www.worldometers.info/coronavirus/')
            soup = BeautifulSoup(await res.text(), 'html.parser')

            counters = [int(c.text.replace(',', '')) for c in soup.find_all(class_='maincounter-number')]
            st_count = [int(c.text.replace(',', '')) for c in soup.find_all(class_='number-table')]
            fmt_st_count = [f'{c:,}'.replace(',', '.') for c in st_count]
            fmt_counters = [f'{c:,}'.replace(',','.') for c in counters]

            updated = re.search('(?<=Last updated: ).+', soup.text).group()
            active = int(counters[0]-(counters[1]+counters[2]))
            active_fmt = f'{active:,}'.replace(',', '.')

            embed = await self.bot.embed(ctx)
            embed.title = trn['emb_title']

            stats = trn['stats_cases'].format(cases=fmt_counters[0])
            stats += trn['stats_deaths'].format(deaths=fmt_counters[1], pcent=counters[1]/counters[0]*100)
            stats += trn['stats_recov'].format(recovered=fmt_counters[2], pcent=counters[2]/counters[0]*100)
            stats += trn['stats_activ'].format(active=active_fmt, pcent=active/counters[0]*100)
            embed.add_field(name=trn['emb_stats'], value=stats)
 
            pac_stats = trn['p_stats_mild'].format(mild=fmt_st_count[0], pcent=st_count[0]/active*100)
            pac_stats += trn['p_stats_crit'].format(critical=fmt_st_count[1], pcent=st_count[1]/active*100)
            embed.add_field(name=trn['emb_p_stats'], value=pac_stats, inline=False)

            embed.set_footer(text=trn['emb_footer'].format(author_name=ctx.author.name), icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.strptime(updated, '%B %d, %Y, %H:%M GMT')
            return await ctx.send(embed=embed)

    @commands.command()
    async def report(self, ctx, member:discord.Member, *, msg):
        trn = await ctx.trn

        async def invalid_report():
            await self.bot.db.update_guild({"_id":ctx.guild.id, "report": None})
            return await ctx.send(trn['err_nset'])

        _guild = await self.bot.db.get_guild(ctx.guild.id)
        
        channel = ctx.guild.get_channel(_guild["report"])

        if not _guild.get("report"):
            return await ctx.send(trn['err_nset'])

        if not channel:
            await invalid_report()

        _rep = await self.bot.embed(ctx)
        _rep.title = trn['rep_title']
        _rep.description = trn['rep_desc'].format(author_mention=ctx.author.mention, member_mention=member.mention, reason=msg)
        
        try:
            await channel.send(embed=_rep)
        except:
            await invalid_report()

        await ctx.send(trn['success'])
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Utils(bot))