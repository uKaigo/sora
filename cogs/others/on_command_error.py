import traceback
from time import time
from hashlib import shake_256
import discord
from discord.ext import commands
from utils.custom import Embed
from utils import menus


class CommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        #pylint: disable=too-many-branches, too-many-statements
        if not ctx.me.permissions_in(ctx.channel).send_messages:
            return

        aliases = {'UnexpectedQuoteError': 'ExpectedCLosingQuoteError'}

        name = aliases.get(error.__class__.__name__, error.__class__.__name__)
        original = error.__cause__
        original_name = original.__class__.__name__

        if isinstance(original, discord.Forbidden):  # pylint: disable=no-else-return
            perms = ctx.me.permissions_in(ctx.channel)
            if perms.embed_links:
                return await ctx.send(ctx.t('no_perm', _e=original_name))
            if not perms.embed_links:
                return await ctx.send(ctx.t('no_embed', _e=original_name))
            return

        elif isinstance(original, menus.CannotReadMessageHistory):
            embed = Embed(ctx, error=True, description=ctx.t('emb_desc', _e=original_name))
            return await ctx.send(embed=embed)

        elif isinstance(error, (commands.CommandNotFound, commands.NotOwner)):
            pass

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)

        elif isinstance(error, (commands.ExpectedClosingQuoteError, commands.UnexpectedQuoteError)):
            quote = error.quote if isinstance(error, commands.UnexpectedQuoteError) else error.close_quote

            embed = Embed(ctx, error=True, title=ctx.t(f'emb_title', _e=name))
            embed.description = ctx.t(f'emb_desc', quote=quote, _e=name)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            perms = [ctx.t(c, _f='perms').title().replace('_', '') for c in error.missing_perms]
            embed = Embed(ctx, error=True, title=ctx.t('emb_title', _e=name))
            embed.description = ctx.t('emb_desc', _e=name, perms=', '.join(perms), s='s' if len(perms)
                                      > 1 else '', oes='ões' if len(perms) > 1 else 'ão')
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            perms = [ctx.t(c, _f='perms').title().replace('_', '') for c in error.missing_perms]

            embed = Embed(ctx, error=True, title=ctx.t('emb_title', _e=name))
            embed.description = ctx.t('emb_desc', _e=name, perms=', '.join(perms), s='s' if len(perms)
                                      > 1 else '', oes='ões' if len(perms) > 1 else 'ão')
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MemberNotFound):
            embed = Embed(ctx, error=True, title=ctx.t('emb_title', _e=name))
            embed.description = ctx.t('emb_desc', _e=name, member=error.argument)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):

            embed = Embed(ctx, error=True, description=ctx.t('invalid', _e=name, arg=error.args[0]))
            embed.title = discord.Embed.Empty
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = Embed(ctx, error=True, title=ctx.t('emb_title', _e=name), description=ctx.t('emb_desc', _e=name))
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CheckFailure):
            return

        else:
            lines = traceback.format_exception(type(error), error, error.__traceback__, 1)
            trace_txt = ''.join(lines)

            code = shake_256(str(time()).replace('.', '').encode()).hexdigest(13)  # pylint: disable=too-many-function-args

            embed = Embed(ctx, error=True)
            embed.description = ctx.t('emb_desc', code=code, error=error, _e='noError')
            await ctx.send(embed=embed)

            ch = self.bot.get_channel(678064736545406996)
            embed = Embed(ctx, error=True)

            embed.description = f'Ocorreu um erro no comando `{ctx.command.qualified_name}` executado por `{ctx.author}`\n\n'
            embed.description += f'Invocação do comando: `{ctx.message.content}`\n\nCódigo: `{code}`\n\n'

            embed.description += f'```{"".join(lines)}```'

            await ch.send(embed=embed)


def setup(bot):
    bot.add_cog(CommandError(bot))
