import discord
from datetime import datetime
import inspect
import psutil
from os import getenv 
from json import load 
from discord.ext import commands

class BotCmds(commands.Cog, name='_bot_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        trn = await ctx.trn
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"]
        embed.description = trn["emb_desc"].format(ping=self.bot.latency*1000)
        await ctx.send(embed=embed)

    @commands.command(aliases=['help'])
    async def ajuda(self, ctx, *, comando=None):
        trn = await ctx.trn
        if comando:
            cmd = self.bot.get_command(comando)
            if cmd:
                lang = await ctx.lang
                with open(f"translation/{lang}/commands.json", encoding='utf-8') as cmds:
                    cmd_trn = load(cmds).get(cmd.qualified_name.replace(" ", "."))
            else:
                cmd_trn = None

            if cmd is None or cmd_trn is None or cmd.hidden:
                embed = await self.bot.erEmbed(ctx, trn["err_nf_title"])
                embed.description = trn["err_nf_desc"].format(cmd=comando)
                return await ctx.send(embed=embed)
            embed = await self.bot.embed(ctx)
            embed.title = trn["emb_title"].format(cmd=cmd_trn["name"].capitalize())

            embed.add_field(name=trn["emb_fld_usage"], value=cmd_trn["usage"].format(ctx.prefix), inline=False)

            aliases = []
            if cmd.aliases:
                for c in cmd.aliases:
                    if c == cmd_trn["name"]:
                        aliases.append(cmd.name)
                    else:
                        aliases.append(c)
                
                embed.add_field(name=trn["emb_fld_aliases"], value=', '.join(aliases), inline=False)

            embed.add_field(name=trn["emb_fld_desc"], value=cmd_trn["description"])

            try:
                if cmd.commands:
                    embed.add_field(name=trn["embed_fld_subc"], value=', '.join([cmd_trn["sub_commands"][name] for c in cmd.commands]), inline=False)
            except:
                pass

            if cmd.parent:
                embed.add_field(name=trn["emb_fld_root"], value=comando.split(' ')[0], inline=False)
            embed.set_footer(text=trn['emb_footer'].format(author_name=ctx.author.name), icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        # Commands -> cmds
        cogs = [self.bot.get_cog(c) for c in self.bot.cogs]
        embed = await self.bot.embed(ctx)
        embed.title = trn["cmds_emb_title"]
        embed.description = trn["cmds_emb_desc"].format(prefix=self.bot.formatPrefix(ctx), author=ctx.author)
        lang = await ctx.lang
        with open(f'translation/{lang}/commands.json', encoding='utf-8') as lng:
            cmds_jsn = load(lng)

        for cog in cogs:
            cogcmd = [f'`{cmds_jsn[c.qualified_name.replace(" ", ".")]["name"]}`' for c in cog.walk_commands() if not c.hidden]
            if not cogcmd:
                continue
            embed.add_field(name=f'{cmds_jsn["_cogs"][cog.qualified_name]} ({len(cogcmd)}):', value=', '.join(cogcmd), inline=False)

        embed.set_footer(text=trn["cmds_emb_footer"].format(author_name=ctx.author.name, prefix=self.bot.formatPrefix(ctx)), icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command(aliases=['bi'])
    async def botinfo(self, ctx):
        trn = await ctx.trn
        embed = await self.bot.embed(ctx)
        embed.set_author(name='Sora Info', icon_url=ctx.me.avatar_url)
        embed.description = trn["desc_intro"]
        embed.description += trn["desc_creation"]
        embed.description += trn["desc_grow"]
        embed.description += trn["desc_love"].format(members=len(self.bot.users))        
        #prf = await ctx.guild_prefix
        #prf = str(prf).replace('None', ctx.prefix)
        #embed.description += trn["desc_prefix"].format(prefix=prf)
        change = trn["ch_lang"].format(prefix=self.bot.formatPrefix(ctx)) if ctx.author.permissions_in(ctx.channel).manage_guild else ''
        lang = await ctx.lang
        embed.description += trn['desc_help'].format(prefix=self.bot.formatPrefix(ctx))
        embed.description += trn["desc_lang"].format(lang=lang.upper(), change=change)
        embed.description += trn['desc_trn']
        await ctx.send(embed=embed)

    @commands.command(aliases=['stats'])
    async def botstats(self, ctx):
        trn = await ctx.trn
        with open(f'translation/{await ctx.lang}/commands.json', encoding='utf-8') as lng:
            time_lang = load(lng)["_time"]
        embed = await self.bot.embed(ctx)
        embed.set_author(name=trn["emb_title"].format(bot_name=self.bot.user.name), icon_url=ctx.me.avatar_url)
        embed.description = trn["emb_desc"].format(author_name=ctx.author.name)
        embed.add_field(name=trn["emb_version"], value=f'`{self.bot.__version__}`')
        embed.add_field(name=trn["emb_uptime"], value=f'`{"".join(self.bot.formatTime(time_lang, self.bot.uptime))}`', inline=False)
        embed.add_field(name=trn["emb_created"], value=f'`{ctx.me.created_at.strftime("%d/%m/%Y %H:%M")}`\n`({"".join(self.bot.getTime(time_lang, ctx.me.created_at))})`', inline=False)
        embed.add_field(name=f'Fui criado por:', value=f'`Kaigo#0833`\nEm: `discord.py {discord.__version__}`')
        mem = psutil.virtual_memory()
        embed.add_field(name=trn["emb_techinfo"], 
        value=f'{trn["techinfo_cpu"]} `{psutil.cpu_percent()}%`\n{trn["techinfo_ram"]} `{mem.used//1024//1024/1024:.1f}/{mem.total//1024//1024/1024:.1f} GB`  ({mem.percent}%)\n{trn["techinfo_hd"]} `{psutil.disk_usage(".").percent}%`',
        inline=False)

        ping = f'{self.bot.latency*1000:.1f}'
        if getenv("HEROKU"):
            host = f'Heroku `({ping}ms)`'
        else:
            host = f'Local `({ping}ms)`'
        embed.add_field(name=trn["emb_host"], value=host, inline=False)

        embed.add_field(name=f'Links:', value=f'{trn["links_inv"]}(https://bit.ly/SoraBot)\n{trn["links_server"]}(https://discord.gg/4YVfJMV)\nSource: [uKaigo/Sora-Bot](https://github.com/uKaigo/Sora-Bot) ', inline=False)
        
        embed.set_footer(text=trn["emb_footer"].format(author_name=ctx.author.name, prefix=self.bot.formatPrefix(ctx)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['ver'])
    async def version(self, ctx):
        trn = await ctx.trn
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"]
        embed.description = trn["emb_desc"]
        embed.add_field(name=trn["emb_version"], value=f'[{self.bot.__version__}]({self.bot.__commit__["html_url"]})', inline=False)
        embed.add_field(name=trn["emb_commiter"], value=f'[{self.bot.__commit__["author"]["login"]}]({self.bot.__commit__["author"]["html_url"]})', inline=False)
        
        hour = datetime.strptime(self.bot.__commit__["commit"]["author"]["date"], '%Y-%m-%dT%H:%M:%SZ')
        hour = self.bot.utc_to_timezone(hour, self.bot.timezone)
        
        with open("assets/config.json") as jsn:
            message_id = load(jsn)["changelog_id"]
        
        g = self.bot.get_guild(675889958262931488)
        if ctx.author in g.members:
            embed.add_field(name=trn["emb_changelog"], value=f'[Link](https://discordapp.com/channels/675889958262931488/676520484820484096/{message_id})', inline=False)
        
        embed.add_field(name=trn["emb_notes"], value=self.bot.__commit__["commit"]["message"], inline=False)
        embed.set_footer(text=trn["emb_footer"].format(author_name = ctx.author.name), icon_url=ctx.author.avatar_url)
        embed.timestamp = hour
        await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx, *, comando=None):
        trn = await ctx.trn
        github = 'https://github.com/uKaigo/Sora-Bot' # Coloque o source do seu bot

        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"] if not comando else trn["emb_title_cmd"].format(obj=comando.replace(" ", "."))
        if not comando:
            embed.description = github
            return await ctx.send(embed=embed)
    
        listeners = dict()
        for c in [self.bot.get_cog(c) for c in self.bot.cogs]:
            for event in c.get_listeners():
                listeners[event[0]] = event[1]

        if not comando in list(listeners):
            cmd = self.bot.get_command(comando)
            if not cmd:
                embed = await self.bot.erEmbed(ctx, trn["err_nf_title"])
                embed.description = trn["err_nf_desc"]
                return await ctx.send(embed=embed)
            cmd_func = cmd.callback
        else:
            cmd_func = listeners[comando]

        cmd_mod = cmd_func.__module__

        code, linha1 = inspect.getsourcelines(cmd_func.__code__)
        linha2 = linha1+(len(code)-1)

        loc = cmd_mod.replace('.', '/') + '.py'
        branch = 'master'
        source = f'{github}/blob/{branch}/{loc}#L{linha1}-L{linha2}'
        embed.description = f'[{branch}/{loc}#L{linha1}]({source})'
        await ctx.send(embed=embed)

def setup(bot): 
    bot.add_cog(BotCmds(bot))
