import discord
from discord.ext import commands


class SupportEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(675889958262931488)
        
        if not payload.channel_id == 676516685192364042 and not payload.guild_id == guild.id:
            return

        if str(payload.emoji) == '🔔':
            cargo = guild.get_role(688526866121883652)
            membro = guild.get_member(payload.user_id)
            if cargo not in membro.roles:
                await membro.add_roles(cargo)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(675889958262931488)
        if not payload.channel_id == 676516685192364042 and not payload.guild_id == guild.id:
            return
        if str(payload.emoji) == '🔔':
            cargo = guild.get_role(688526866121883652)
            membro = guild.get_member(payload.user_id)
            if cargo in membro.roles:
                await membro.remove_roles(cargo)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == 676523018943594572 and not message.content.startswith('>'):
            await message.add_reaction('👍')
            return await message.add_reaction('👎') 
        if message.channel.id == 676520526910324768:
            return await message.author.add_roles(message.guild.get_role(676517824411336745), reason=f'{message.author} verificado!')


def setup(bot):
    bot.add_cog(SupportEvents(bot))