import discord
import traceback
import json
import re
from discord.ext import commands

class CommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): #pylint: disable=too-many-branches, too-many-statements
        aliases = {'UnexpectedQuoteError': 'ExpectedCLosingQuoteError'}

        name = aliases.get(error.__class__.__name__, error.__class__.__name__)

        if isinstance(error, (commands.CommandNotFound, commands.NotOwner)):
            pass

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)

        elif isinstance(error, (commands.ExpectedClosingQuoteError, commands.UnexpectedQuoteError)):
            quote = error.quote if isinstance(error, commands.UnexpectedQuoteError) else error.close_quote

            embed = self.bot.erEmbed(ctx, ctx.t(f'emb_title', _e=name))
            embed.description = ctx.t(f'emb_desc', quote=quote, _e=name)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            perms = [ctx.t(c, _f='perms').title().replace('_', '') for c in error.missing_perms]
            embed = self.bot.erEmbed(ctx, ctx.t('emb_title', _e=name))
            embed.description= ctx.t('emb_desc', _e=name, perms=', '.join(perms), s='s' if len(perms) > 1 else '', oes='ões' if len(perms) > 1 else 'ão')
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            perms = [ctx.t(c, _f='perms').title().replace('_', '') for c in error.missing_perms]

            embed = self.bot.erEmbed(ctx, ctx.t('emb_title', _e=name))
            embed.description = ctx.t('emb_desc', _e=name, perms=', '.join(perms), s='s' if len(perms) > 1 else '', oes='ões' if len(perms) > 1 else 'ão')
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            if 'Member' in error.args[0] and 'not found' in error.args[0]:
                trn = ctx.t('memberNotFound.emb_title', _e=name)
                member = error.args[0].split('"')[1]

                embed = self.bot.erEmbed(ctx, ctx.t('memberNotFound.emb_title', _e=name))
                embed.description = ctx.t('memberNotFound.emb_desc', _e=name, member=member)
                return await ctx.send(embed=embed)

            embed = self.bot.erEmbed(ctx)
            embed.title = discord.Embed.Empty
            embed.description = ctx.t('invalid', _e=name, arg=error.args[0])
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = self.bot.erEmbed(ctx, ctx.t('emb_title', _e=name))
            embed.description = ctx.t('emb_desc', _e=name)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CheckFailure):
            return

        else:    
            name = 'noError'
            if hasattr(error, 'original'):
                er_name = type(error.original).__name__

                if isinstance(error.original, discord.Forbidden):
                    embed = self.bot.erEmbed(ctx, ctx.t(f'{er_name}.emb_title', _e=name))
                    embed.description = ctx.t(f'{er_name}.emb_desc', _e=name)
                    if ctx.author.permissions_in(ctx.channel).manage_channels:
                        embed.description += ctx.t(f'{er_name}.desc_perm', _e=name, channel_mention=ctx.channel.mention)
                    else:
                        embed.description += ctx.t(f'{er_name}.desc_noperm', _e=name, channel_mention=ctx.channel.mention)
                    return await ctx.author.send(embed=embed)

            lines = traceback.format_exception(type(error), error, error.__traceback__, 2)
            trace_txt = ''.join(lines)
            
            ch = self.bot.get_channel(678064736545406996)
            embed = self.bot.erEmbed(ctx)
            embed.description=f'Ocorreu um erro.\n\nServidor: {str(ctx.guild)} ({ctx.guild.id if ctx.guild else str(ctx.author)})\nMensagem: `{ctx.message.content}`\nAutor: {ctx.author}'
            embed.add_field(name='Erro:', value=trace_txt[:1024])
            await ch.send(embed=embed)
            
            embed = self.bot.erEmbed(ctx)
            embed.description = ctx.t('emb_desc', _e=name)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CommandError(bot))