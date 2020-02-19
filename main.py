import discord
import assets.database as database
import assets.functions as functions
import asyncio
import aiohttp
from datetime import datetime
from os import getenv, listdir
import json
from pathlib import Path
from discord.ext import commands, tasks

    
if not getenv("HEROKU"):
    ### Caso for executar no seu computador, digite `pip install python-dotenv` ###
    from dotenv import load_dotenv
    env_f = Path('./assets/') / '.env'
    load_dotenv(dotenv_path=env_f)
token = getenv('token')

with open('assets/config.json') as cnf:
    config = json.load(cnf)
    config["prefix"] = config["prefix"] if getenv("HEROKU") else "sc." # Canary é rodado localmente

class Sora(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or(config["prefix"]), case_insensitive=True)
        self.token = 'Bela tentativa, quase me pegou...'

        # Cores
        self.color = 0xBA3C51
        self.ecolor = 0xDD2E44
        self.neutral = 0x36393F

        # Requests
        self.session = aiohttp.ClientSession(loop=self.loop)
        
        # Variáveis internas
        self.__started_in__ = None
        self.lang = 'pt-br'
        self.__commit__ = ''
        #self.db = database.Database(getenv('mongo_uri'), 'Sora')
        self.emotes = dict()
        self.nfimg = 'https://i.imgur.com/byuoWoJ.png'
        
        # Funções
        self.sec2hours = functions.sec2hours
        self.formatTime = functions.formatTime
        self.sec2time = functions.sec2time
        self.getTime = functions.getTime
        self.paginator = functions.paginator

        # Versão do bot
        with open("assets/config.json") as cnf:
            jsn = json.load(cnf)
            self.__version__ = jsn["version"]

        # Carregamento de cogs
        self.remove_command('help')
        for fldr in listdir('cogs'):
            for file in listdir(f'cogs/{fldr}'):
                if file.startswith('_') or not file.endswith('.py'):
                    continue
                file = file.replace(".py", "")
                try:
                    self.load_extension(f'cogs.{fldr}.{file}')
                except Exception as e:
                    print(f'Falha ao carregar [{fldr}/{file}]: ({type(e).__name__}) {e}')
                else:
                    print(f'{fldr.capitalize()}.{file} carregado com sucesso.')

    def __repr__(self):
        return f'<{__name__}.Sora guilds={len(self.guilds)} users={len(self.users)}> '

    def formatPrefix(self, ctx):
        prefix = ctx.prefix if not str(self.user.id) in ctx.prefix else f'@{ctx.me} '
        return ctx.prefix.replace(ctx.prefix, prefix)

    # Embeds
    def embed(self, ctx, invisible=False):
        color = self.neutral if invisible else self.color
        emb = discord.Embed(color=color)
        emb.set_footer(text=f'Executado por {ctx.author.name}', icon_url=ctx.author.avatar_url)
        emb.timestamp = ctx.message.created_at
        return emb

    def erEmbed(self, ctx, error='Erro!'):
        emb = discord.Embed(title=f':x: | {error}', color=self.ecolor)
        emb.set_footer(text=f'Executado por {ctx.author.name}', icon_url=ctx.author.avatar_url)
        emb.timestamp = ctx.message.created_at
        return emb

    async def on_message(self, message):
        return

    async def on_ready(self):
        print('---------- Bot Online -----------')
        print(f'Nome: {self.user.name}')
        print(f'Id: {self.user.id}')
        print(f'Usuários: {len(self.users) - len([c for c in self.users if c.bot])}')
        print(f'Bots: {len([c for c in self.users if c.bot])}')
        print(f'Guilds: {len(self.guilds)}')
        print('---------------------------------')
        ############

        # Servidor de emojis, verifique os emojis usados pelo bot para não dar erro. (Caso for usar)
        for emoji in self.get_guild(675889958262931488).emojis:
            self.emotes[emoji.name] = emoji
        await self.change_presence(activity=discord.Activity(name='minha ajuda', type=1, url='https://twitch.tv/ukaigo'))
        self.__started_in__ = datetime.utcnow()

        # Embaixo do uptime, pq isso não é necessário antes.
        git_name, git_token = getenv("git_token").split(":")
        auth = aiohttp.BasicAuth(git_name, git_token, 'utf-8')
        aux = "Merge branch"
        index = 0
        while aux.startswith("Merge branch"):
            s = await self.session.get("https://api.github.com/repos/uKaigo/Sora-Bot/commits", auth=auth)
            j = await s.json()
            j = j[index]
            aux = j["commit"]["message"]
            index += 1
        self.__commit__ = j

    pings = property(functions.__getpings__, functions.__cantset__, functions.__cantdel__)
    uptime = property(functions.__getuptime__, functions.__cantset__, functions.__cantdel__)

bot = Sora()

@bot.check
async def blacklist(ctx):
    with open('assets/users_banned.json') as bn:
        jsn = json.load(bn)
    if str(ctx.author.id) in jsn and not ctx.author.id == bot.owner_id:
        reason = jsn[str(ctx.author.id)]
        embed = discord.Embed(title=f':x: | Sem permissão!', description=f'Você foi banido de usar qualquer comando meu, o motivo é:\n`{reason}`', color=bot.ecolor)
        await ctx.send(embed=embed)
        return False
    return True

if __name__ == '__main__':
    try:
        bot.run(token)
    except KeyboardInterrupt: 
        pass
