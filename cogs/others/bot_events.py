from datetime import datetime 
import discord
from discord.ext import commands


class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log = self.bot.get_guild(675889958262931488).get_channel(697240163050586203)
        embed = discord.Embed(color=self.bot.color)
        embed.title = 'Novo servidor!'
        embed.description = f'Nome: `{guild.name}`\nId: `{guild.id}`\nDono: `{guild.owner}`\nRegiao: `{guild.region}`'
        await log.send(embed=embed)
        await self.bot.db.guilds.new(guild.id)
        if guild.region.value == 'brazil':
            await self.bot.db.guilds.update({'_id': guild.id, 'lang': 'pt-br'})

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log = self.bot.get_guild(675889958262931488).get_channel(697240163050586203)
        embed = discord.Embed(color=self.bot.ecolor)
        embed.title = 'Removido de um servidor!'
        embed.description = f'Nome: `{guild.name}`\nId: `{guild.id}`\nDono: `{guild.owner}`'
        await log.send(embed=embed)
        await self.bot.db.guilds.delete(guild.id)

    @commands.Cog.listener()
    async def on_guild_post(self):
        time = datetime.now().strftime('%H:%M:%S')
        print(f'[TOP.GG] {time} - Guilds atualizados: {len(self.bot.guilds)}')

def setup(bot):
    bot.add_cog(BotEvents(bot))
