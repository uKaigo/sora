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
        trn = await self.bot.get_error(error, ctx)

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
            embed = await self.bot.erEmbed(ctx, trn["emb_title"])
            if suggestions and not isinstance(error, commands.NotOwner):
                embed.description = trn["mean"]
                embed.description += f'\n'.join(suggestions)
                return await ctx.send(embed=embed)
            else:
                return

        elif isinstance(error, commands.MissingRequiredArgument):
            translation = await ctx.translation
            embed = await self.bot.erEmbed(ctx, trn["emb_title"])
            embed.add_field(name=trn["emb_use"], value=translation["usage"].format(ctx.prefix), inline=False)
            embed.add_field(name=trn["emb_desc"], value=translation["description"])
            embed.set_footer(text=trn["emb_footer"].format(author_name=ctx.author.name), icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.UnexpectedQuoteError):
            quote = error.quote if isinstance(error, commands.UnexpectedQuoteError) else error.close_quote
            
            embed = await self.bot.erEmbed(ctx, trn["emb_title"])
            embed.description = trn["emb_desc"].format(quote=quote)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            lang = await ctx.lang
            with open(f'translation/{lang}/perms.json', encoding='utf-8') as lng:
                prms = json.load(lng)
            perms = [prms[c].title() for c in error.missing_perms]
            embed = await self.bot.erEmbed(ctx, trn["emb_title"])
            embed.description= trn["emb_desc"].format(perms=", ".join(perms), s="s" if len(perms) > 1 else "", oes="ões" if len(perms) > 1 else "ão")
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            lang = await ctx.lang
            with open(f'translation/{lang}/perms.json', encoding='utf-8') as lng:
                prms = json.load(lng)
            perms = [prms.get(c, c).title().replace('_', '') for c in error.missing_perms]

            embed = await self.bot.erEmbed(ctx, trn["emb_title"])
            embed.description = trn["emb_desc"].format(perms=', '.join(perms), s='s' if len(perms) > 1 else '', oes='ões' if len(perms) > 1 else 'ão')
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            if "Member" in error.args[0] and "not found" in error.args[0]:
                trn = trn["memberNotFound"]
                member = error.args[0].split('"')[1]

                embed = await self.bot.erEmbed(ctx, trn["emb_title"])
                embed.description = trn["emb_desc"].format(member=member)
                return await ctx.send(embed=embed)
            embed = await self.bot.erEmbed(ctx)
            embed.title = discord.Embed.Empty
            embed.description = trn["invalid"].format(arg=error.args[0])
    
        elif isinstance(error, commands.NoPrivateMessage):
            embed = await self.bot.erEmbed(ctx, trn["emb_title"])
            embed.description = trn['emb_desc']
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.CheckFailure):
            return

        else:    
            if hasattr(error, 'original'):
                try:
                    trn = trn[type(error.original).__name__]
                except:
                    trn = trn
                if isinstance(error.original, discord.Forbidden):
                    embed = await self.bot.erEmbed(ctx, trn["emb_title"])
                    embed.description = trn["emb_desc"]
                    if ctx.author.permissions_in(ctx.channel).manage_channels:
                        embed.description += trn["desc_perm"].format(channel_mention = ctx.channel.mention)
                    else:
                        embed.description += trn["desc_noperm"].format(channel_mention=ctx.channel.mention)
                    return await ctx.author.send(embed=embed)
            
                if isinstance(error.original, NotImplementedError):
                    embed = await self.bot.erEmbed(ctx, trn["emb_title"])
                    embed.description = trn["emb_desc"]
                    return await ctx.send(embed=embed)

            lines = traceback.format_exception(type(error), error, error.__traceback__, 2)
            trace_txt = ''.join(lines)
            
            ch = self.bot.get_channel(678064736545406996)
            embed = await self.bot.erEmbed(ctx)
            embed.description=f'Ocorreu um erro.\n\nServidor: {str(ctx.guild)} ({ctx.guild.id if ctx.guild else str(ctx.author)})\nMensagem: `{ctx.message.content}`\nAutor: {ctx.author}'
            embed.add_field(name='Erro:', value=trace_txt[:1024])
            await ch.send(embed=embed)
            
            embed = await self.bot.erEmbed(ctx)
            embed.description = trn["emb_desc"]
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CommandError(bot))