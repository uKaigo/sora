import discord
from assets.models.custom import SoraContext
from discord.ext import commands


class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = []
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Bloquear bots
        if message.author.bot:
            return
        
        await self.bot.wait_until_ready()

        # Interpretar comandos
        ctx = await self.bot.get_context(message, cls=SoraContext)
        if message.content.replace('!', '') == ctx.me.mention and ctx.guild:
            ctx._lang = await self.bot.db.guild_get(message.guild.id, 'lang')
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
