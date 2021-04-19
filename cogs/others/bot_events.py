from datetime import datetime
import discord
from discord.ext import commands


class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log = self.bot.get_guild(675889958262931488).get_channel(697240163050586203)
        embed = discord.Embed(color=self.bot.color)
        embed.title = 'Novo servidor!'
        embed.description = f'Nome: `{guild.name}`\nId: `{guild.id}`\nDono: `{guild.owner}`\nRegiao: `{guild.region}`'
        embed.description += f'\nUnavailable: {guild.unavailable}'
        await log.send(embed=embed)
        await self.bot.db.guilds.new(guild.id)
        if guild.region.value == 'brazil':
            await self.bot.db.guilds.update({'_id': guild.id, 'lang': 'pt-br'})

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log = self.bot.get_guild(675889958262931488).get_channel(697240163050586203)
        embed = discord.Embed(color=self.bot.ecolor)
        embed.title = 'Removido de um servidor!'
        embed.description = f'Nome: `{guild.name}`\nId: `{guild.id}`\nDono: `{guild.owner}`'
        await log.send(embed=embed)
        await self.bot.db.guilds.delete(guild.id)

    @commands.Cog.listener()
    async def on_guild_post(self):
        time = datetime.now().strftime('%H:%M:%S')
        print(f'[TOP.GG] {time} - Guilds atualizados: {len(self.bot.guilds)}')

    @commands.Cog.listener()
    async def on_zuraaa_vote(self, user):
        print(f'{user} votou no Sora!')
        print(f'Atualmente com {self.bot.zuraaa_vote_streak}')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = self.bot.get_guild(675889958262931488).get_channel(814340967674019880)

        embed = discord.Embed(
            title=f'Comando "{ctx.command.qualified_name}" executado.',
            color=self.bot.color
        )

        embed.set_author(name=f'{ctx.author} ({ctx.author.id})', icon_url=ctx.author.avatar_url)

        embed.add_field(name='Servidor', inline=False, value=(
            f'\> Nome: {ctx.guild.name}\n'
            f'\> ID: {ctx.guild.id}\n'
            f'\> Dono: {ctx.guild.owner} ({ctx.guild.owner.id})'
        ))

        embed.add_field(name='Canal', inline=False, value=(
            f'\> Nome: {ctx.channel.name}\n'
            f'\> ID: {ctx.channel.id}\n'
            f'\> NSFW: {ctx.channel.nsfw}'
        ))

        embed.add_field(name='Mensagem', inline=False, value=(
            f'\> Conteúdo: "{discord.utils.escape_markdown(ctx.message.content)}"\n'
            f'\> ID: {ctx.message.id}\n'
            f'\> URL: [Link]({ctx.message.jump_url})'
        ))

        embed.timestamp = ctx.message.created_at
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(BotEvents(bot))
