from discord.ext import commands

class SupportEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.channel_id == 676516685192364042:
            return

        guild = self.bot.get_guild(675889958262931488)

        if str(payload.emoji) == '🔔':
            role = guild.get_role(688526866121883652)
            member = guild.get_member(payload.user_id)
            if not role in member.roles:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.channel_id == 676516685192364042:
            return

        guild = self.bot.get_guild(675889958262931488)

        if str(payload.emoji) == '🔔':
            role = guild.get_role(688526866121883652)
            member = guild.get_member(payload.user_id)
            if role in member.roles:
                await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channels = [676523018943594572, 729831163518255124]

        if message.channel.id in channels and not message.content.startswith('>'):
            await message.add_reaction('👍')
            return await message.add_reaction('👎')

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        if not guild.id == 675889958262931488: return
        entry = await self.bot.get_guild(675889958262931488).fetch_ban(member)
        self.bot.support_bans[member.id] = entry

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if not guild.id == 675889958262931488: return
        try:
            del(self.bot.support_bans[user.id])
        except KeyError:
            pass

def setup(bot):
    bot.add_cog(SupportEvents(bot))