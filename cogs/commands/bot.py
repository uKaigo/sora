import psutil
from datetime import datetime
import discord
from discord.ext import commands
from utils.custom import SoraHelp, Embed

class BotCmds(commands.Cog, name='_bot_cog'):
    def __init__(self, bot):
        self.bot = bot
        bot.old_help = bot.help_command
        bot.help_command = SoraHelp()
        bot.help_command.cog = self

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        await ctx.send(ctx.t('text', ping=round(self.bot.latency*1000, 2)))

    @commands.command(aliases=['stats'])
    async def botstats(self, ctx):
        time_lang = ctx.t('_time', _nc=1)

        process = psutil.Process()
        embed = self.bot.embed(ctx)
        embed.set_author(name=ctx.t('emb_title', bot_name=self.bot.user.name), icon_url=ctx.me.avatar_url)
        embed.description = ctx.t('emb_desc', author_name=ctx.author.name)
        embed.add_field(name=ctx.t('emb_version'), value=f'`{self.bot.__version__}`')
        embed.add_field(name=ctx.t('emb_uptime'), value=f'`{self.bot.formatTime(time_lang, self.bot.uptime)}`', inline=False)
        embed.add_field(name=ctx.t('emb_created'), value=f'`{ctx.me.created_at.strftime("%d/%m/%Y %H:%M")}`\n`({"".join(self.bot.getTime(time_lang, ctx.me.created_at))})`', inline=False)
        embed.add_field(name=ctx.t('emb_creator'), value=f'`Kaigo#0833`\n`discord.py {discord.__version__}`')
        mem = psutil.virtual_memory()
        embed.add_field(name=ctx.t('emb_techinfo'), 
        value=f'{ctx.t("techinfo_cpu")} `{process.cpu_percent()}%`\n{ctx.t("techinfo_ram")} `{process.memory_info().rss//1024//1024/1024*1000:.1f} MB/{mem.total//1024//1024/1024:.1f} GB`  ({process.memory_percent():.2f}%)\n{ctx.t("techinfo_hd")} `{psutil.disk_usage(".").percent}%`',
        inline=False)

        ping = f'{self.bot.latency*1000:.1f}'
        if self.bot.is_heroku:
            host = f'Heroku `({ping}ms)`'
        else:
            host = f'Local `({ping}ms)`'
        embed.add_field(name=ctx.t('emb_host'), value=host, inline=False)

        embed.add_field(name=ctx.t('emb_total'), value=ctx.t('total_value', guilds=len(self.bot.guilds), users=len(set(self.bot.users))))
        
        embed.add_field(name=f'Links:', value=f'{ctx.t("links_inv")}(https://is.gd/SoraBot)\n{ctx.t("links_server")}(https://discord.gg/4YVfJMV)\nSource: [uKaigo/Sora-Bot](https://github.com/uKaigo/Sora-Bot) ', inline=False)
        
        await ctx.send(embed=embed)

def setup(bot): 
    bot.add_cog(BotCmds(bot))
