import discord
from discord.ext import commands

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Bloquear bots e dm
        if message.author.bot:
            return
        
        await self.bot.wait_until_ready()

        # Servidor de suporte
        if message.channel.id == 676523018943594572 and not message.content.startswith('>'):
            await message.add_reaction('👍')
            return await message.add_reaction('👎') 
        if message.channel.id == 676520526910324768:
            return await message.author.add_roles(message.guild.get_role(676517824411336745), reason=f'{message.author} verificado!')
        
        # Interpretar comandos
        ctx = await self.bot.get_context(message)
        if message.content.replace('!', '') == ctx.me.mention:
            ctx.prefix = ctx.me.mention
            ctx.command = self.bot.get_command('botinfo')
            ctx.args = None
            ctx.author = message.author
        await self.bot.invoke(ctx)


def setup(bot):
    bot.add_cog(OnMessage(bot))