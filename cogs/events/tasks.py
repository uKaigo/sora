import discord
from itertools import cycle
from discord.ext import tasks, commands


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

        # Todas as presenças e o número delas.
        self.presences = cycle([
            (1, 'minha ajuda'),
            (2, 'seus comandos'),
            (3, 'o youtube'),
            (1, 'coronga virus'),
        ])

        self.ch_presence.start()

    @tasks.loop(seconds=120)
    async def ch_presence(self):
        tp, name = next(self.presences)
        await self.bot.change_presence(activity=discord.Activity(name=name, type=tp, url='https://twitch.tv/ukaigo'))


def setup(bot):
    bot.add_cog(Tasks(bot))