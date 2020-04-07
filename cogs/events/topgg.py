import dbl
import discord
from datetime import datetime
from os import getenv
from discord.ext import commands


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dblpy = dbl.DBLClient(self.bot, getenv("dbl_token"), autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        time = datetime.now().strftime('%H:%M:%S')
        print(f'[TOP.GG] {time} - Guilds atualizados: {len(self.bot.guilds)}')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):   
        print(data)

def setup(bot):
    bot.add_cog(TopGG(bot))