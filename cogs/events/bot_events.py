import discord
import asyncio
import aiohttp
from re import search
from datetime import datetime 
from os import getenv
from discord.ext import commands


class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.__started_in__:
            print('Bot retomado!')
            return
        print('---------- Bot Online -----------')
        print(f'Nome: {self.bot.user.name}')
        print(f'Id: {self.bot.user.id}')
        print(f'Usuários: {len(self.bot.users) - len([c for c in self.bot.users if c.bot])}')
        print(f'Bots: {len([c for c in self.bot.users if c.bot])}')
        print(f'Guilds: {len(self.bot.guilds)}')
        print('---------------------------------')
        ############

        # Servidor de emojis, verifique os emojis usados pelo bot para não dar erro. (Caso for usar)
        for emoji in self.bot.get_guild(675889958262931488).emojis:
            self.bot.emotes[emoji.name] = emoji
        
        await self.bot.change_presence(activity=discord.Activity(name='minha ajuda', type=1, url='https://twitch.tv/ukaigo'))

        self.bot.__started_in__ = datetime.utcnow()

        # Embaixo do uptime, pq isso não é necessário antes.
        # Função para o so.version
        git_name, git_token = getenv("git_token").split(":")
        auth = aiohttp.BasicAuth(git_name, git_token, 'utf-8')
        aux = "Merge"
        index = 0
        while aux.split(" ")[0] in ["Merge", "setver"]:
            s = await self.bot.session.get("https://api.github.com/repos/uKaigo/Sora-Bot/commits", auth=auth)
            j = await s.json()
            j = j[index]
            aux = j["commit"]["message"]
            index += 1
        self.bot.__commit__ = j

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log = self.bot.get_guild(675889958262931488).get_channel(697240163050586203)
        embed = discord.Embed(color=self.bot.color)
        embed.title = 'Novo servidor!'
        embed.description = f'Nome: `{guild.name}`\nId: `{guild.id}`\nDono: `{guild.owner}`\nRegiao: `{guild.region}`'
        await log.send(embed=embed)
        await self.bot.db.new_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log = self.bot.get_guild(675889958262931488).get_channel(697240163050586203)
        embed = discord.Embed(color=self.bot.ecolor)
        embed.title = 'Removido de um servidor!'
        embed.description = f'Nome: `{guild.name}`\nId: `{guild.id}`\nDono: `{guild.owner}`'
        await log.send(embed=embed)
        await self.bot.db.delete_guild(guild.id)

def setup(bot):
    bot.add_cog(BotEvents(bot))
