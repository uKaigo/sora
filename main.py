import discord
import assets.functions as functions
from pytz import timezone
from os import getenv, listdir
import json
from aiohttp import ClientSession
from assets.database import Database
from typing import Optional
from pathlib import Path
from discord.ext import commands

    
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
        self.db = Database(getenv("mongo_uri"), "Sora")

        # Cores
        self.color = 0xBA3C51
        self.ecolor = 0xDD2E44
        self.neutral = 0x36393F
        
        # Variáveis internas
        self.__started_in__ = None
        self.__commit__ = ''
        self.session = ClientSession(loop=self.loop)
        self.lang = 'pt-br'
        self.emotes = dict()
        self.timezone = timezone("America/Sao_Paulo")
        self.nfimg = 'https://i.imgur.com/byuoWoJ.png' # Not Found Image
        
        # Funções
        self.sec2hours = functions.sec2hours
        self.formatTime = functions.formatTime
        self.sec2time = functions.sec2time
        self.getTime = functions.getTime
        self.paginator = functions.paginator
        self.utc_to_timezone = functions.utc_to_timezone

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
    
    # Tradução
    async def get_lang(self, ctx:Optional[commands.Context]=None, cmd=True):
        lang = await self.db.get_language(ctx.guild.id)
        if cmd:
            with open(f"translation/commands_{lang}.json", encoding="utf-8") as trns:
                cmd = json.load(trns).get(ctx.command.qualified_name.replace(" ", "."), None)
            return cmd
        return lang

    async def get_error(self, error, ctx):
        aliases = {"NotOwner": "CommandNotFound", "UnexpectedQuoteError": "ExpectedClosingQuoteError"}
        try:
            lang = await ctx.lang
            with open(f'translation/errors_{lang}.json', encoding='utf-8') as trns:
                loaded = json.load(trns)
                
                return loaded.get(aliases.get(type(error).__name__, type(error).__name__), loaded["noError"])

        except Exception as e:
            print(e)
            return None

    # Embeds
    async def embed(self, ctx, invisible=False):
        color = self.neutral if invisible else self.color
        emb = discord.Embed(color=color)
        with open(f"translation/commands_{await ctx.lang}.json", encoding='utf-8') as jsn:
            trn = json.load(jsn)["_executed_by"]
        emb.set_footer(text=trn.format(author_name=ctx.author.name), icon_url=ctx.author.avatar_url)
        emb.timestamp = ctx.message.created_at
        return emb

    async def erEmbed(self, ctx, error='_err_no_title'):
        with open(f"translation/commands_{await ctx.lang}.json", encoding='utf-8') as jsn:
            loaded = json.load(jsn)
            title = loaded.get(error, error)
            trn = loaded["_executed_by"]
        emb = discord.Embed(title=f':x: | {title}', color=self.ecolor)
        emb.set_footer(text=trn.format(author_name=ctx.author.name), icon_url=ctx.author.avatar_url)
        emb.timestamp = ctx.message.created_at
        return emb

    async def on_message(self, message):
        return

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
