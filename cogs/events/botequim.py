import discord 
from re import search
from discord.ext import commands


class Botequim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild.id != 492338791802208266:
            return
        
        full_msg = message.content.replace('\n', '').replace(' ', '').lower()

        if search('cheap', full_msg) or search('paehc', full_msg):
            for role in message.author.roles:
                if role.name == '@everyone':
                    continue
                await message.author.remove_roles(role)
            await message.delete()
            return await message.author.add_roles(message.guild.get_role(700833376780943383))



def setup(bot):
    bot.add_cog(Botequim(bot))
