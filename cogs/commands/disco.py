import discord
import typing
from discord.ext import commands 

class Disco(commands.Cog, name='Discord'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='{}avatar (membro)', description='Retorna seu avatar ou de um membro.')
    async def avatar(self, ctx, membro:typing.Optional[discord.Member]):
        member = membro or ctx.author 
        embed = self.bot.embed(ctx)
        embed.title = f'Avatar de {member.name}:'
        if not membro:
            embed.description = f'{ctx.author.mention}, aqui está seu avatar.'
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(usage='{}userinfo (membro)', description='Exibe informações de um membro.')
    async def userinfo(self, ctx, *, membro:typing.Optional[discord.Member]):
        membro = membro or ctx.author
        cor = membro.color if str(membro.color) != '#000000' else self.bot.color

        embed = self.bot.embed(ctx)
        embed.title = f'Aqui estão algumas informações sobre {membro}.'
        embed.color = cor

        embed.set_author(name=f'Userinfo | {membro.name}', icon_url=membro.avatar_url)
        embed.add_field(name='Tag:', value=str(ctx.author), inline=False)
        embed.add_field(name='Id:', value=str(ctx.author.id), inline=False)
        statuses = {"online": "Online", "dnd": "Não perturbar", "idle": "Ausente", "offline": "Offline"}
        embed.add_field(name='Status:', value=str(self.bot.emotes[f"sora_{str(membro.status)}"]) + f" {':iphone:' if membro.is_on_mobile() else ''} {statuses[str(membro.status)]}", inline=False)
        embed.add_field(name='Criado em:', value=f'{membro.created_at.strftime("%d/%m/%Y %H:%M")} ({self.bot.getTime(membro.created_at)[0].replace(", ", "").replace("e ", "")} atrás)', inline=False)
        embed.add_field(name='Entrou em:', value=f'{membro.joined_at.strftime("%d/%m/%Y %H:%M")} ({self.bot.getTime(membro.joined_at)[0].replace(", ", "").replace("e ", "")} atrás)', inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Disco(bot))