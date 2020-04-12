import discord
from datetime import datetime
import inspect
import psutil
from re import sub, split
from os import getenv 
from json import load 
from discord.ext import commands
from assets.models import menus
import itertools

class HelpPaginator(menus.baseMenu):
    def __init__(self, page_trn, title, prefix, _index, pages):
        super().__init__(pages, title, '')
        self.prefix = prefix
        self._pagec = page_trn
        if _index != -1:
            self._index = _index
            self.should_add_reactions = lambda: False
        else:
            self._index = _index+1

    @property
    async def embed(self):
        current = self.pages[self._index]

        cog = current[0]
        commands = current[1]

        embed = await self.bot.embed(self.ctx)
        
        if self.should_add_reactions():
            embed.set_author(name=self._pagec.format(page=self._index+1, max=len(self.pages)))
        
        embed.title = self._title.format(cog=cog)
        
        for cmd, description in commands:
            embed.add_field(name=cmd.format(self.prefix), value=description, inline=False)
        
        return embed

class SoraHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"aliases": ['ajuda']})
        self._help_index = -1

    async def command_not_found(self, string):
        # For Cogs
        with open(f"translation/{await self.context.lang}/commands.json", encoding='utf-8') as trns:
            trns = load(trns)
            translated = [trns["_cogs"][c].lower() for c in trns["_cogs"]]
            translated.sort()
            if string.lower() in translated or (string.isnumeric() and 0 <= int(string) <= len(translated)):
                if string.isnumeric():
                    return str(string)
                return str(translated.index(string.lower()))

        trn = await self.context.trn
        return trn['notfound'].format(cmd=string)

    async def subcommand_not_found(self, command, string):
        trn = await self.context.trn
        if isinstance(command, commands.Group):
            return trn['sub_notfound'][0].format(cmd=command.name, sub=string) 
        return trn['sub_notfound'][1].format(sub=command.name)

    async def send_error_message(self, error):
        if error.isnumeric():
            self._help_index = int(error)
            await self.send_bot_help([])
            return
        await self.context.send(error)

    async def send_bot_help(self, mapping):
        ctx = self.context
        trn = await ctx.trn

        def key(cmd):
            return cmd.cog_name or trn['no_cat']

        cmds = await self.filter_commands(ctx.bot.commands, sort=True, key=key)

        pages = []

        _cogs = []
        _cog_list = ["_bot_cog", "_disco_cog", "_fun_cog", "_mod_cog", "_music_cog", "_utils_cog"]
        for cog, commands in itertools.groupby(cmds, key=key):
            commands = sorted(commands, key = lambda m: m.name)
            if not commands:
                continue

            with open(f"translation/{await ctx.lang}/commands.json", encoding='utf-8') as trns:
                trns = load(trns)
                
                _cogs.append(cog)
                cog = trns["_cogs"][cog]
                commands = [[trns[c.name]["usage"]] + [trns[c.name]["description"]] for c in commands]

            pages.append((cog, commands))

        if not self._help_index == -1:
            try:
                _pg = _cog_list[self._help_index]
                if not _pg == _cogs[self._help_index]:
                    self._help_index = -1
            except:
                self._help_index = -1
        _index = self._help_index
        self._help_index = -1

        paginator = HelpPaginator(trn['page_c'], trn['emb_title'], self.clean_prefix, _index, pages)
        await paginator.start(ctx)

class BotCmds(commands.Cog, name='_bot_cog'):
    def __init__(self, bot):
        self.bot = bot
        bot.old_help = bot.help_command
        bot.help_command = SoraHelp()
        bot.help_command.cog = self

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        trn = await ctx.trn
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"]
        embed.description = trn["emb_desc"].format(ping=self.bot.latency*1000)
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
        if not hasattr(self.bot, '__commit__'):
            return await ctx.send(trn['no_commit'])
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"]
        embed.description = trn["emb_desc"]
        embed.add_field(name=trn["emb_version"], value=f'[{self.bot.__version__}]({self.bot.__commit__["html_url"]})', inline=False)
        embed.add_field(name=trn["emb_commiter"], value=f'[{self.bot.__commit__["author"]["login"]}]({self.bot.__commit__["author"]["html_url"]})', inline=False)
        
        hour = datetime.strptime(self.bot.__commit__["commit"]["author"]["date"], '%Y-%m-%dT%H:%M:%SZ')
        hour = self.bot.utc_to_timezone(hour, self.bot.timezone)
        
        with open("assets/json/config.json") as jsn:
            message_id = load(jsn)["changelog_id"]
        
        g = self.bot.get_guild(675889958262931488)
        if ctx.author in g.members:
            embed.add_field(name=trn["emb_changelog"], value=f'[Link](https://discordapp.com/channels/675889958262931488/676520484820484096/{message_id})', inline=False)
        
        embed.add_field(name=trn["emb_notes"], value=self.bot.__commit__["commit"]["message"], inline=False)
        embed.set_footer(text=trn["emb_footer"].format(author_name = ctx.author.name), icon_url=ctx.author.avatar_url)
        embed.timestamp = hour
        await ctx.send(embed=embed)


def setup(bot): 
    bot.add_cog(BotCmds(bot))
