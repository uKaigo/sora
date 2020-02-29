import discord
from discord.ext import commands


class DiscordEvents(commands.Cog, name=''):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        bctx = await self.bot.get_context(before) # Isso é pra tirar a reação do não existente
        try:
            if not bctx.invoked_with in self.bot.all_commands:
                await after.remove_reaction('❌', bctx.me)
        except:
            pass
        await self.bot.process_commands(after)

def setup(bot):
    bot.add_cog(DiscordEvents(bot))