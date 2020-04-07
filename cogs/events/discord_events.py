import discord
from discord.ext import commands


class DiscordEvents(commands.Cog, name=''):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = []

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        bctx = await self.bot.get_context(before) # Isso é pra tirar a reação do não existente
        try:
            if not bctx.invoked_with in self.bot.all_commands:
                await after.remove_reaction('❌', bctx.me)
        except:
            pass
        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(675889958262931488)
        channel = discord.utils.get(guild.channels, id=676516685192364042)
        
        aaa = await self.guild.get_channel(676522528469942292).send(payload.emoji)

        if channel is None:
            return
        if not payload.channel_id == 676516685192364042:
            return
        if payload.channel_id == None:
            return
        
        if payload.user_id in self.cooldown:
            return

        if '<:sora_online:677666240524976128>'  == str(payload.emoji):
                guild = self.bot.get_guild(payload.guild_id)
                cargo = guild.get_role(688526866121883652)
                membro = guild.get_member(payload.user_id)
                if cargo not in membro.roles:
                    await membro.add_roles(cargo)
                    self.cooldown.append(payload.user_id)
                    self.cooldown.remove(payload.user_id)
                break

def setup(bot):
    bot.add_cog(DiscordEvents(bot))
