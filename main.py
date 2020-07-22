from json import load
from os import getenv, listdir
from aiohttp import ClientSession, __version__ as aiohttp_version
from sys import version as py_version
from datetime import datetime
from discord import Embed, Activity
from discord.ext import commands
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


class Sora(commands.AutoShardedBot):
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        super().__init__(command_prefix=get_prefix, case_insensitive=True)
        self.db = Database(getenv('mongo_uri'), 'Sora')

        # Cores
        self.color = 0xBA3C51
        self.ecolor = 0xDD2E44
        self.neutral = 0x2F3136 

        # Variáveis internas
        self._started_date = self.session = None
        self.apis = json()
        self._translation_cache = dict()
        self.is_heroku = is_heroku
        self.emotes = dict()
        self.config = config
        self.nfimg = 'https://i.imgur.com/byuoWoJ.png' # Not Found Image

        # Funções
        self.sec2hours = functions.sec2hours
        self.formatTime = functions.formatTime
        self.sec2time = functions.sec2time
        self.paginator = functions.paginator
        self.getTime = functions.getTime

        self.loop.run_until_complete(self.define_session())

        # Versão do bot
        self.version = self.config['version']
        
    def __repr__(self) -> str:
        return f'<{__name__}.Sora guilds={len(self.guilds)} users={len(self.users)}> '

    async def define_session(self):
        if not hasattr(self, 'session') or not self.session:
            headers = {
                'User-Agent': 'SoraBot/{} (https://github.com/uKaigo)'.format(self.version),
                'X-Powered-By': 'aiohttp {}/Python {}'.format(aiohttp_version, py_version)
                }
            self.session = ClientSession(headers=headers, connector=self.http.connector, loop=self.loop)

    async def close(self):
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

        # Servidor de emojis, verifique os emojis usados pelo bot para não dar erro. (Caso for usar)
        for emoji in self.get_guild(675889958262931488).emojis:
            if emoji.name.startswith('sora_'):
                self.emotes[emoji.name] = emoji

        await self.change_presence(activity=Activity(name='minha ajuda', type=1, url='https://twitch.tv/ukaigo'))

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

        super().run(token, **kwargs)

    pings = property(functions.__getpings__,
                     functions.__cantset__, functions.__cantdel__)
    uptime = property(functions.__getuptime__,
                      functions.__cantset__, functions.__cantdel__)


bot = Sora()

if __name__ == '__main__':
    try:
        bot.run(getenv('token'))
    except KeyboardInterrupt:
        pass
