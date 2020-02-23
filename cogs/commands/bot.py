import discord
from datetime import datetime
from pytz import timezone as pytzTz
import inspect
import psutil
import os
import json
from discord.ext import commands

class BotCmds(commands.Cog, name='Bot'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='{}ping', description='Envia a latência do bot.', aliases=['pong'])
    async def ping(self, ctx):
        embed = self.bot.embed(ctx)
        embed.title = '🏓 | Ping!'
        embed.description = f'Neste momento estou com `{self.bot.latency*1000:.1f}ms`'
        await ctx.send(embed=embed)

    @commands.command(usage='{}ajuda (comando) (subcomando)', description='Exibe informações sobre um comando', aliases=['help'])
    async def ajuda(self, ctx, *, comando=None):
        if comando:
            cmd = self.bot.get_command(comando)
            # Esses "erro = True/False" é para não repetir código.
            erro = False
            if cmd is None:
                erro = True
            if cmd.hidden:
                erro = True
            if erro:
                embed = self.bot.erEmbed(ctx, 'Comando não encontrado.')
                embed.description = f'O comando `{comando}` não foi encontrado!\n Verifique ortografia, se você informou o comando pai ou se o comando realmente existe.'
                return await ctx.send(embed=embed)

            embed = self.bot.embed(ctx)
            embed.title=f'Ajuda | {cmd.name.capitalize()}'

            embed.add_field(name='Uso:', value=cmd.usage.format(ctx.prefix), inline=False)

            if cmd.aliases:
                embed.add_field(name='Abreviações:', value=', '.join(cmd.aliases), inline=False)

            embed.add_field(name='Descrição:', value=cmd.description)

            try:
                if cmd.commands:
                    embed.add_field(name='Subcomandos:', value=', '.join([c.name for c in cmd.commands]), inline=False)
            except:
                pass

            if cmd.parent:
                embed.add_field(name='Comando pai:', value=comando.split(' ')[0], inline=False)

            return await ctx.send(embed=embed)

        cogs = [self.bot.get_cog(c) for c in self.bot.cogs]
        embed = self.bot.embed(ctx)
        embed.title = 'Sora | Comandos'
        embed.description = f'Nota: Argumentos opcionais são pulados para o proximo argumento, por exemplo, se você digitar `{self.bot.formatPrefix(ctx)}purge @{ctx.author} 5`, com a menção ou não, deletará 5 mensagens.'

        for cog in cogs:
            cogcmd = [f'`{c.name}`' for c in cog.get_commands() if not c.hidden]
            if not cogcmd:
                continue
            embed.add_field(name=f'{cog.qualified_name} ({len(cogcmd)}):', value=', '.join(cogcmd), inline=False)

        embed.set_footer(text=f'{ctx.author.name} • Digite `{self.bot.formatPrefix(ctx)}ajuda [comando]`', icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command(usage='{}botinfo', description='Exibe as informações do bot')
    async def botinfo(self, ctx):
        embed = self.bot.embed(ctx)
        embed.description = f'Olá, {ctx.author.name}. Aqui está algumas informações sobre mim.'
        embed.set_author(name=f"{self.bot.user.name} | Info", icon_url=ctx.me.avatar_url)
        embed.add_field(name="Estou na versão", value=f'`{self.bot.__version__}`')
        embed.add_field(name=f'Estou online por:', value=f'`{"".join(self.bot.formatTime(self.bot.uptime))}`', inline=False)
        embed.add_field(name=f'Fui criado em:', value=f'`{ctx.me.created_at.strftime("%d/%m/%Y ás %H:%M")}`\n`({"".join(self.bot.getTime(ctx.me.created_at))})`', inline=False)
        embed.add_field(name=f'Fui criado por:', value=f'`Kaigo#0833`\nEm: `discord.py {discord.__version__}`')
        
        mem = psutil.virtual_memory()
        embed.add_field(name=f'Informações técnicas:', 
        value=f'Porcentagem da cpu: `{psutil.cpu_percent()}%`\nRam usada: `{mem.used//1024//1024/1024:.1f}/{mem.total//1024//1024/1024:.1f} GB`  ({mem.percent}%)\nUso de disco: `{psutil.disk_usage(".").percent}%`',
        inline=False)

        ping = f'{self.bot.latency*1000:.1f}'
        if os.getenv("HEROKU"):
            host = f'Heroku `({ping}ms)`'
        else:
            host = f'Local `({ping}ms)`'
        embed.add_field(name=f'Hospedagem:', value=host, inline=False)

        embed.add_field(name=f'Links:', value='Convite: [Clique](https://bit.ly/SoraBot)\nSource: [uKaigo/Sora-Bot](https://github.com/uKaigo/Sora-Bot) \nServidor: [Entre](https://discord.gg/4YVfJMV)', inline=False)
        
        embed.set_footer(text=f'{ctx.author.name} • Digite `{self.bot.formatPrefix(ctx)}comandos`', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(usage='{}total', description='Mostra as estatísticas do bot')
    async def total(self, ctx):
        embed = self.bot.embed(ctx)
        embed.title = f'Atualmente com `{len(self.bot.users)}` usuários, `{len(self.bot.guilds)}` servidores, `{len(self.bot.emojis)}` emojis e `{len([c for c in self.bot.get_all_channels()])}` canais.'
        await ctx.send(embed=embed)

    @commands.command(usage='{}version', description='Mostra as informações da versão atual do bot atual.')
    async def version(self, ctx):
        embed = self.bot.embed(ctx)
        embed.title = 'Sora | Versão'
        embed.description = 'Algumas informações sobre minha versão, e o commit atual.'
        embed.add_field(name='Versão:', value=f'[{self.bot.__version__}]({self.bot.__commit__["html_url"]})', inline=False)
        embed.add_field(name='Commit feito por:', value=f'[{self.bot.__commit__["author"]["login"]}]({self.bot.__commit__["author"]["html_url"]})', inline=False)
        hour = datetime.strptime(self.bot.__commit__["commit"]["author"]["date"], '%Y-%m-%dT%H:%M:%SZ')
        hour = self.bot.utc_to_timezone(hour, self.bot.timezone)
        with open("assets/config.json") as jsn:
            message_id = json.load(jsn)["changelog_id"]
        embed.add_field(name='Mensagem da changelog:', value=f'[Clique aqui](https://discordapp.com/channels/675889958262931488/676520484820484096/{message_id})', inline=False)
        embed.add_field(name='Notas desta versão:', value=self.bot.__commit__["commit"]["message"], inline=False)
        embed.set_footer(text=f'{ctx.author.name} • Commit feito', icon_url=ctx.author.avatar_url)
        embed.timestamp = hour
        await ctx.send(embed=embed)

    @commands.command(usage='{}source [comando]', description='Mostra o código de um comando.')
    async def source(self, ctx, *, comando=None):
        github = 'https://github.com/uKaigo/Sora-Bot' # Coloque o source do seu bot
        embed = self.bot.embed(ctx)
        embed.title = 'Aqui está meu source:' if not comando else f'Aqui está o source do comando {comando.replace(" ", ".")}:'
        if not comando:
            embed.description = github
            return await ctx.send(embed=embed)

        cmd = self.bot.get_command(comando)
        if not cmd:
            embed = self.bot.erEmbed(ctx, "Comando inválido!")
            embed.description = 'O comando que você digitou, não existe.\nVerifique ortografia ou se o (sub)comando existe.'
            return await ctx.send(embed=embed)

        cmd_func = cmd.callback
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
