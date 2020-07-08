import discord
from discord.ext import commands
from utils import SoraContext

class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Bloquear bots
        if message.author.bot:
            return
        
        await self.bot.wait_until_ready()

        # Interpretar comandos
        ctx = await self.bot.get_context(message, cls=SoraContext)

        if ctx.guild:
            ctx._lang = await self.bot.db.guilds.get(ctx.guild.id, 'lang')
        else:
            ctx._lang = 'en-us'

        if message.content.replace('!', '') == ctx.me.mention and ctx.guild:
            prefix = await self.bot.get_prefix(ctx.message)
            await ctx.send(ctx.t('_mention', prefix=prefix[-1], _nc=1))

        await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        bctx = await self.bot.get_context(before) # Isso é pra tirar a reação do não existente
        try:
            if not bctx.invoked_with in self.bot.all_commands:
                await after.remove_reaction('❌', bctx.me)
        except:
            pass
        ctx = await self.bot.get_context(after, cls=SoraContext)
        await self.bot.invoke(ctx)

def setup(bot):
    bot.add_cog(DiscordEvents(bot))
