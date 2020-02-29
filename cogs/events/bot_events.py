import discord
import aiohttp
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

        # Requests
        self.bot.session = aiohttp.ClientSession(loop=self.bot.loop)

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
    bot.add_cog(BotEvents(bot))