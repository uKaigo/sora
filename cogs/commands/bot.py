import discord
from datetime import datetime
import inspect
import psutil
from assets.models.custom import SoraHelp
from re import sub, split
from os import getenv 
from json import load 
from discord.ext import commands
from assets.models import menus
import itertools

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
        with open(f'translation/{ctx.lang}/commands.json', encoding='utf-8') as lng:
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
        if getenv("DYNO"):
            host = f'Heroku `({ping}ms)`'
        else:
            host = f'Local `({ping}ms)`'
        embed.add_field(name=trn["emb_host"], value=host, inline=False)

        embed.add_field(name=f'Links:', value=f'{trn["links_inv"]}(https://bit.ly/SoraBot)\n{trn["links_server"]}(https://discord.gg/4YVfJMV)\nSource: [uKaigo/Sora-Bot](https://github.com/uKaigo/Sora-Bot) ', inline=False)
        
        embed.set_footer(text=trn["emb_footer"].format(author_name=ctx.author.name, prefix=self.bot.formatPrefix(ctx)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

def setup(bot): 
    bot.add_cog(BotCmds(bot))
