import discord
from json import load
from os import getenv, listdir
from aiohttp import ClientSession, __version__ as aiohttp_version
from sys import version_info as py_version
from datetime import datetime
from asyncio import create_task, get_running_loop
from discord import Embed, Activity
from discord.ext import commands
from ksoftapi import Client
from utils import functions
from utils.classes import json
from utils.database import Database

is_heroku = bool(getenv('DYNO'))

if not is_heroku: # Carregamento do canary
    from dotenv import load_dotenv
    from pathlib import Path
    env = Path('.') / '.env'
    load_dotenv(dotenv_path=env)

with open('utils/config.json') as cnf:
    config = load(cnf)
    config['prefix'] = config['prefix'] if is_heroku else 'sc.'

async def get_prefix(bot, message):
    if message.guild:
        prefix = await bot.db.guilds.get(message.guild.id, 'prefix') or config['prefix']
        return commands.when_mentioned_or(prefix)(bot, message)
    return commands.when_mentioned_or('')(bot, message)

intents = discord.Intents()
for intent_to_enable in config['intents']:
    setattr(intents, intent_to_enable, True)

class Sora(commands.AutoShardedBot):
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        super().__init__(command_prefix=get_prefix, case_insensitive=True, intents=intents)
        self.db = Database(getenv('MONGO_URI'), 'Sora')

        # Cores
        self.color = 0xBA3C51
        self.ecolor = 0xDD2E44
        self.neutral = 0x2F3136 

        # Variáveis internas
        self._started_date = self.session = None
        self._translation_cache = dict()
        self.apis = json()
        self.is_heroku = is_heroku
        self.emotes = dict()
        self.config = config
        self.support_bans = {}

        # Funções
        self.sec2hours = functions.sec2hours
        self.formatTime = functions.formatTime
        self.sec2time = functions.sec2time
        self.paginator = functions.paginator
        self.getTime = functions.getTime

        # Versão do bot
        self.version = self.config['version']

        self.apis.ksoft = Client(getenv('KSOFT_TOKEN'), loop=self.loop)

        self.loop.create_task(self.async_init())

    def __repr__(self) -> str:
        return f'<{__name__}.Sora guilds={len(self.guilds)} users={len(self.users)}> '

    async def async_init(self):
        if not hasattr(self, 'session') or not self.session:
            headers = {
                'User-Agent': 'SoraBot/{} (https://github.com/uKaigo)'.format(self.version),
                'X-Powered-By': 'aiohttp {0}/Python {1.major}.{1.minor}.{1.micro}'.format(aiohttp_version, py_version)
            }
            self.session = ClientSession(headers=headers, connector=self.http.connector, loop=self.loop)

        await self.wait_until_ready()

        for emoji in self.get_guild(777716631253024768).emojis:
            self.emotes[emoji.name] = emoji

        bans = await self.get_guild(675889958262931488).bans()
        for entry in bans:
            self.support_bans[entry.user.id] = entry

    async def close(self):
        await self.apis.ksoft.close()
        await self.apis['ffz'].close()
        await self.session.close()
        await super().close()

    def formatPrefix(self, ctx) -> str:
        prefix = ctx.prefix if not str(self.user.id) in ctx.prefix else f'@{ctx.me} '
        return ctx.prefix.replace(ctx.prefix, prefix)

    async def on_message(self, message):
        return

    async def on_ready(self):
        if self._started_date:
            print('Bot retomado!')
            return
        print(f'{f" {self.user.name} ":-^33}')
        print(f'{f"Id: {self.user.id}":^33}')
        bots = [member for member in self.users if member.bot]
        print(f'{f"Usuários: {len(self.users) - len(bots)}":^33}')
        print(f'{f"Bots: {len(bots)}":^33}')
        print(f'{f"Guilds: {len(self.guilds)}":^33}')
        print('---------------------------------')
        ############

        self._started_date = datetime.utcnow()

    def run(self, token, **kwargs):
        for folder in listdir('cogs'):
            for _file in listdir(f'cogs/{folder}'):
                if _file.startswith('_') or not _file.endswith('.py'):
                    continue
                _file = _file.replace('.py', '')
                try:
                    self.load_extension(f'cogs.{folder}.{_file}')
                except Exception as e:
                    print(f'[{folder}.{_file}] -> {type(e).__name__}: {e}')
                else:
                    print(f'[{folder}.{_file}] -> Carregado.')
        try:
            self.load_extension('zuraaaVoteChecker')
        except Exception as e:
            print(f'[zuraaaVoteChecker] -> {type(e).__name__}: {e}')
        else:
            print(f'[zuraaaVoteChecker] -> Carregado.')

        super().run(token, **kwargs)

    pings = property(functions.__getpings__,
                     functions.__cantset__, functions.__cantdel__)
    uptime = property(functions.__getuptime__,
                      functions.__cantset__, functions.__cantdel__)


bot = Sora()

@bot.check
async def check_ban(ctx):
    if ctx.author.id in bot.support_bans:
        reason = bot.support_bans[ctx.author.id].reason
        await ctx.send(f"Você está banido./You're banned.\n```{reason}```")
        return False
    return True

if __name__ == '__main__':
    try:
        bot.run(getenv('TOKEN'))
    except KeyboardInterrupt:
        pass
