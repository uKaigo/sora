from os import getenv
from itertools import cycle
import discord
from discord.ext import tasks, commands
from dbl import DBLClient

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if bot.is_heroku:
            self.dblpy = DBLClient(self.bot, getenv('DBL_TOKEN'), autopost=True)

        # Todas as presenças e o número delas.
        self.presences = cycle([
            (2, 'so.help'),
            (1, 'meus comandos'),
            (1, 'prefixo so.') 
        ])

        self.ch_presence.start() # pylint: disable=no-member

    @tasks.loop(minutes=2)
    async def ch_presence(self):
        tp, name = next(self.presences)
        await self.bot.change_presence(activity=discord.Activity(name=name, type=tp, url='https://twitch.tv/ukaigo'))

    @ch_presence.before_loop # pylint: disable=no-member
    async def init_presence(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Tasks(bot))
