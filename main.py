import json
import logging
from os import getenv, listdir
from aiohttp import ClientSession
from datetime import datetime
from discord import Embed, Activity, utils
from discord.ext import commands
from utils import functions
from utils.database import Database

# Configurando o logger
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

is_heroku = bool(getenv('DYNO'))

if not is_heroku: # Carregamento do canary
    from dotenv import load_dotenv
    from pathlib import Path
    env = Path('.') / '.env'
    load_dotenv(dotenv_path=env)

with open('utils/config.json') as cnf:
    config = json.load(cnf)
    config['prefix'] = config['prefix'] if is_heroku else 'sc.'

async def get_prefix(bot, message):
    if message.guild:
        prefix = await bot.db.guilds.get(message.guild.id, 'prefix') or config['prefix']
        return commands.when_mentioned_or(prefix)(bot, message)
    return commands.when_mentioned_or(config['prefix'])(bot, message)


class Sora(commands.AutoShardedBot):
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        super().__init__(command_prefix=get_prefix, case_insensitive=True)
        self.db = Database(getenv('mongo_uri'), 'Sora')

        # Cores
        self.color = 0xBA3C51
        self.ecolor = 0xDD2E44
        self.neutral = 0x36393F

        # Variáveis internas
        self.__started_in__ = None
        self.is_heroku = is_heroku
        self._translation_cache = dict()
        self.session = None
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
        self.__version__ = self.config['version']
        
        for fldr in listdir('cogs'):
            for _file in listdir(f'cogs/{fldr}'):
                if _file.startswith('_') or not _file.endswith('.py'):
                    continue
                _file = _file.replace('.py', '')
                try:
                    self.load_extension(f'cogs.{fldr}.{_file}')
                except Exception as e:
                    print(f'[{fldr}.{_file}] -> {type(e).__name__}: {e}')
                else:
                    print(f'[{fldr}.{_file}] -> Carregado.')

    def __repr__(self) -> str:
        return f'<{__name__}.Sora guilds={len(self.guilds)} users={len(self.users)}> '

    async def define_session(self):
        if not hasattr(self, 'session') or not self.session:
            self.session = ClientSession(loop=self.loop)

    async def close(self):
        await self.session.close()
        self.loop.close()
        await super().close()

    def formatPrefix(self, ctx) -> str:
        prefix = ctx.prefix if not str(self.user.id) in ctx.prefix else f'@{ctx.me} '
        return ctx.prefix.replace(ctx.prefix, prefix)

    # Embeds
    def embed(self, ctx, invisible=False) -> Embed:
        # Cor do embed
        color = self.neutral if invisible else self.color

        emb = Embed(color=color)

        emb.set_footer(text=ctx.t('_executed_by', author_name=ctx.author.name, _nc=1),
                       icon_url=ctx.author.avatar_url)
        
        return emb

    def erEmbed(self, ctx, error='_err_no_title') -> Embed:
        emb = Embed(title=f':x: | {ctx.t(error, _nc=1)}', color=self.ecolor)
        emb.set_footer(text=ctx.t('_executed_by', author_name=ctx.author.name, _nc=1),
                       icon_url=ctx.author.avatar_url)
        return emb

    async def on_message(self, message):
        return

    async def on_ready(self):
        if self.__started_in__:
            print('Bot retomado!')
            return
        print(f'{f" {self.user.name} ":-^33}')
        print(f'{f"Id: {self.user.id}":^33}')
        bots = list(filter(lambda m: m.bot, self.users))
        print(f'{f"Usuários: {len(self.users) - len(bots)}":^33}')
        print(f'{f"Bots: {len(bots)}":^33}')
        print(f'{f"Guilds: {len(self.guilds)}":^33}')
        print('---------------------------------')
        ############

        # Servidor de emojis, verifique os emojis usados pelo bot para não dar erro. (Caso for usar)
        for emoji in self.get_guild(675889958262931488).emojis:
            self.emotes[emoji.name] = emoji
        
        await self.change_presence(activity=Activity(name='minha ajuda', type=1, url='https://twitch.tv/ukaigo'))

        self.__started_in__ = datetime.utcnow()

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
