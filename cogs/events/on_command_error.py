import discord
import traceback
import json
import re
from time import time 
from discord.ext import commands

class CommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): #pylint: disable=too-many-branches, too-many-statements
        if not ctx.me.permissions_in(ctx.channel).send_messages:
            return

        aliases = {'UnexpectedQuoteError': 'ExpectedCLosingQuoteError'}

        name = aliases.get(error.__class__.__name__, error.__class__.__name__)
        original = error.__cause__ 
        original_name = original.__class__.__name__

        if isinstance(original, discord.Forbidden): # pylint: disable=no-else-return
            perms = ctx.me.permissions_in(ctx.channel)
            if perms.embed_links:
                return await ctx.send(ctx.t('no_perm', _e=original_name))
            if not perms.embed_links: 
                return await ctx.send(ctx.t('no_embed', _e=original_name))
            return

        elif isinstance(error, (commands.CommandNotFound, commands.NotOwner)):
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
            if 'Member' in error.args[0]:
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
            lines = traceback.format_exception(type(error), error, error.__traceback__, 1)
            trace_txt = ''.join(lines)

            code = hex(int(str(time()).replace('.', ''))).replace('0x', '')

            await ctx.send(ctx.t('emb_desc', code=code, _e='noError'))

            ch = self.bot.get_channel(678064736545406996)
            embed = self.bot.erEmbed(ctx)

            embed.description = f'Ocorreu um erro no comando `{ctx.command.qualified_name}` executado por `{ctx.author}`\n\n'
            embed.description += f'Invocação do comando: `{ctx.message.content}`\n\nCódigo: `{code}`\n\n'

            embed.description += f'```{"".join(lines)}```'

            await ch.send(embed=embed)
            

def setup(bot):
    bot.add_cog(CommandError(bot))