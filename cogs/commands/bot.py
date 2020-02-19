import discord
from datetime import datetime
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
        embed.add_field(name=f'Fui criado em:', value=f'`{ctx.me.created_at.strftime("%d/%m/%Y as %H:%M")}`\n`({"".join(self.bot.getTime(ctx.me.created_at))})`', inline=False)
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
        embed.add_field(name='Versão:', value=self.bot.__version__, inline=False)
        embed.add_field(name='Notas desta versão:', value=self.bot.__commit__["commit"]["message"])
        await ctx.send(embed=embed)

def setup(bot): 
    bot.add_cog(BotCmds(bot))
