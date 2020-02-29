import discord
import traceback
import json
import re
from discord.ext import commands

class CommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner):
            try:
                await ctx.message.add_reaction('❌')
            except:
                pass
            suggestions = []

            pat = '.*?'.join(map(re.escape, ctx.invoked_with))
            regex = re.compile(pat, flags=re.IGNORECASE)

            for c in self.bot.all_commands:
                r = regex.search(c)
                if r:
                    if c.startswith(ctx.invoked_with):
                        suggestions.append(f'`{self.bot.formatPrefix(ctx)}{c}`')
            embed = self.bot.erEmbed(ctx, "Comando não encontrado!")
            if suggestions and not isinstance(error, commands.NotOwner):
                embed.description = 'Você quis dizer:\n'
                embed.description += f'\n'.join(suggestions)
                return await ctx.send(embed=embed)
            else:
                return

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = self.bot.erEmbed(ctx, f'"{str(error.param).split(":")[0]}" não informado')
            embed.add_field(name='Uso:', value=ctx.command.usage.format(ctx.prefix), inline=False)
            embed.add_field(name='Descrição:', value=ctx.command.description)
            embed.set_footer(text=f'{ctx.author.name} • [obrigatório] (opcional) <arquivo>', icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.UnexpectedQuoteError):
            quote = error.quote if isinstance(error, commands.UnexpectedQuoteError) else error.close_quote
            
            embed = self.bot.erEmbed(ctx, 'Parâmetro inválido.')
            embed.description = f'Por favor, retire qualquer `{quote}` dos parâmetros'
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            lang = self.bot.lang
            with open(f'translation/perms_{lang}.json', encoding='utf-8') as lng:
                prms = json.load(lng)
            perms = [prms[c].title() for c in error.missing_perms]

            embed = self.bot.erEmbed(ctx, 'Sem permissão.')
            embed.description=f'Você precisa da{"s" if len(perms) > 1 else ""} permiss{"ões" if len(perms) > 1 else "ão"} `{", ".join(perms)}` para executar esse comando'
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            lang = self.bot.lang
            with open(f'translation/perms_{lang}.json', encoding='utf-8') as lng:
                prms = json.load(lng)
            perms = [prms[c].title() for c in error.missing_perms]

            embed = self.bot.erEmbed(ctx, 'Sem permissão.')
            embed.description = f'Eu preciso da{"s" if len(perms) > 1 else ""} permiss{"ões" if len(perms) > 1 else "ão"} `{", ".join(perms)}` para executar esse comando'
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            if "Member" in error.args[0] and "not found" in error.args[0]:
                member = error.args[0].split('"')[1]

                embed = self.bot.erEmbed(ctx, 'Membro inválido.')
                embed.description = f'O membro `{member}` não foi encontrado.\nVerifique ortografia ou se o membro está no servidor.'
                return await ctx.send(embed=embed)
            return await ctx.send(f'Argumento inválido.\n{error.args[0]}')
    
        elif isinstance(error, commands.NoPrivateMessage):
            embed = self.bot.erEmbed(ctx, "Canal errado!")
            embed.description = "Este comando não pode ser usado em DM's."
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.CheckFailure):
            return

        else:    
            if hasattr(error, 'original'):
                if isinstance(error.original, discord.Forbidden):
                    embed = self.bot.erEmbed(ctx, 'Sem permissão.')
                    embed.description = f'Desculpe te mandar mensagem no dm, também não gosto disso!\n'
                    if ctx.author.permissions_in(ctx.channel).manage_channels:
                        embed.description += f'Mas parece que você não me deu permissão pra falar no {ctx.channel.mention}.\n'
                        embed.description += 'Por favor, me dê essa permissão ou tente usar em outro canal.'
                    else:
                        embed.description += f'Mas eu não tenho permissão pra falar no canal do comando, peça a algum superior para me deixar falar no {ctx.channel.mention}! (ou apenas use outro canal)'
                    return await ctx.author.send(embed=embed)
            
                if isinstance(error.original, NotImplementedError):
                    embed = self.bot.erEmbed(ctx, "Comando em desenvolvimento!")
                    embed.description = 'Este comando ainda não foi desenvolvido ou está em manutenção. Aguarde futuras atualizações.'
                    return await ctx.send(embed=embed)

            lines = traceback.format_exception(type(error), error, error.__traceback__, 2)
            trace_txt = ''.join(lines)
            ch = self.bot.get_channel(678064736545406996)
            embed = discord.Embed(title=f':x: | Erro', 
            description=f'Ocorreu um erro.\n\nServidor: {str(ctx.guild)} ({ctx.guild.id if ctx.guild else ""})\nMensagem: `{ctx.message.content}`\nAutor: {ctx.author}',
            color=self.bot.ecolor)
            embed.add_field(name='Erro:', value=trace_txt[:1024])
            await ch.send(embed=embed)
            embed = discord.Embed(title=":x: | Erro",
            description=f'Ocorreu um erro desconhecido durante a execução do comando.', color=self.bot.ecolor)
            embed.set_footer(text=f'Executado por {ctx.author.name}', icon_url=ctx.author.avatar_url)
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CommandError(bot))