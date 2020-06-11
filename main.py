import discord
from assets.models import functions
from os import getenv, listdir
import json
from aiohttp import ClientSession
from assets.models.database import Database
from typing import Optional
from pathlib import Path
from discord.ext import commands

is_heroku = bool(getenv('DYNO'))

if not is_heroku: # Carregamento do canary
    from dotenv import load_dotenv
    env = Path('./assets/') / '.env'
    load_dotenv(dotenv_path=env)

with open('assets/json/config.json') as cnf:
    config = json.load(cnf)
    config['prefix'] = config['prefix'] if is_heroku else 'sc.'

async def get_prefix(bot, message):
    if message.guild:
        prefix = await bot.db.guild_get(message.guild.id, 'prefix') or config['prefix']
        return commands.when_mentioned_or(prefix)(bot, message)
    return commands.when_mentioned_or(config['prefix'])(bot, message)


class Sora(commands.AutoShardedBot):
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
        self.session = ClientSession(loop=self.loop)
        self.emotes = dict()
        self.config = config
        self.nfimg = 'https://i.imgur.com/byuoWoJ.png' # Not Found Image

        # Funções
        self.sec2hours = functions.sec2hours
        self.formatTime = functions.formatTime
        self.sec2time = functions.sec2time
        self.getTime = functions.getTime
        self.paginator = functions.paginator
        self.utc_to_timezone = functions.utc_to_timezone

        # Versão do bot
        self.__version__ = self.config['version']

        # Carregamento de cogs
        for fldr in listdir('cogs'):
            for _file in listdir(f'cogs/{fldr}'):
                if _file .startswith('_') or not _file.endswith('.py'):
                    continue
                _file = _file.replace('.py', '')
                try:
                    self.load_extension(f'cogs.{fldr}.{_file}')
                except Exception as e:
                    print(f'Falha ao carregar [{fldr}/{_file}]: ({type(e).__name__}) {e}')
                else:
                    print(f'{fldr.capitalize()}.{_file} carregado com sucesso.')

    def __repr__(self) -> str:
        return f'<{__name__}.Sora guilds={len(self.guilds)} users={len(self.users)}> '

    def formatPrefix(self, ctx) -> str:
        prefix = ctx.prefix if not str(self.user.id) in ctx.prefix else f'@{ctx.me} '
        return ctx.prefix.replace(ctx.prefix, prefix)

    # Tradução

    async def get_lang(self, guild_id) -> str:
        return await self.db.guild_get(guild_id, 'lang')

    async def get_translation(self, ctx) -> str:
        lang = ctx.lang
        command_name = ctx.command.qualified_name
        with open(f'translation/{lang}/commands.json', encoding='utf-8') as trns:
            cmd = json.load(trns).get(command_name)
        return cmd

    # Embeds
    async def embed(self, ctx, invisible=False) -> discord.Embed:
        # Cor do embed
        color = self.neutral if invisible else self.color

        emb = discord.Embed(color=color)

        with open(f'translation/{ctx.lang}/commands.json', encoding='utf-8') as jsn:
            trn = json.load(jsn)['_executed_by']
        
        emb.set_footer(text=trn.format(author_name=ctx.author.name),
                       icon_url=ctx.author.avatar_url)
        
        emb.timestamp = ctx.message.created_at
        return emb

    async def erEmbed(self, ctx, error='_err_no_title') -> discord.Embed:
        with open(f'translation/{ctx.lang}/commands.json', encoding='utf-8') as jsn:
            loaded = json.load(jsn)
            title = loaded.get(error, error)
            trn = loaded['_executed_by']
        
        emb = discord.Embed(title=f':x: | {title}', color=self.ecolor)
        emb.set_footer(text=trn.format(author_name=ctx.author.name),
                       icon_url=ctx.author.avatar_url)
        emb.timestamp = ctx.message.created_at
        return emb

    async def on_message(self, message):
        return

    pings = property(functions.__getpings__,
                     functions.__cantset__, functions.__cantdel__)
    uptime = property(functions.__getuptime__,
                      functions.__cantset__, functions.__cantdel__)


bot = Sora()


@bot.check
async def blacklist(ctx):
    with open('assets/json/users_banned.json') as bn:
        jsn = json.load(bn)
    if str(ctx.author.id) in jsn and not ctx.author.id == bot.owner_id:
        reason = jsn[str(ctx.author.id)]
        embed = await bot.embed(ctx, "Sem permissão!")
        embed.description = f'Você foi banido de usar qualquer comando meu!\nMotivo: `{reason}`'
        await ctx.send(embed=embed)
        return False
    return True

@bot.before_invoke
async def set_lang(ctx):
    if not ctx.guild:
        ctx._lang = 'en-us'
    else:
        ctx._lang = await bot.db.guild_get(ctx.guild.id, 'lang')

if __name__ == '__main__':
    try:
        bot.run(getenv('token'))
    except KeyboardInterrupt:
        pass
