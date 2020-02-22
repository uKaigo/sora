import discord
import typing
import json
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
        bot = 'o bot ' if membro.bot else ""
        embed.title = f'Aqui estão algumas informações sobre {bot}{membro.name}.'
        embed.color = cor

        embed.set_author(name=f'Userinfo | {membro.name}', icon_url=membro.avatar_url)

        apelido = f'\n**Apelido:** {membro.nick}' if membro.nick else ''
        embed.add_field(name='Membro:', value=f'**Tag:** {membro}{apelido}\n**ID:** {membro.id}')
        
        statuses = {"online": "Online", "dnd": "Não perturbar", "idle": "Ausente", "offline": "Offline"}
        status = str(self.bot.emotes[f"sora_{str(membro.status)}"]) + f" {':iphone:' if membro.is_on_mobile() else ''} **{statuses[str(membro.status)]}**"
        if membro.activity:
            activity = ["Jogando:", "Transmitindo:", "Ouvindo:", "Assistindo:", "Custom:"]
            if membro.activity.type.value == 1:
                status += f'\n**{activity[membro.activity.type.value]}** [{membro.activity.name}]({membro.activity.url})'
            else:
                status += f'\n**{activity[membro.activity.type.value]}** {membro.activity.name}'
        embed.add_field(name='Status:', value=status, inline=False)
        
        embed.add_field(name='Data:', value=f'**Que criou a conta:** {membro.created_at.strftime("%d/%m/%Y %H:%M")} ({self.bot.getTime(membro.created_at)[0].replace(", ", "").replace("e ", "")} atrás)\n**Que entrou no server:** {membro.joined_at.strftime("%d/%m/%Y %H:%M")} ({self.bot.getTime(membro.joined_at)[0].replace(", ", "").replace("e ", "")} atrás)', inline=False)
        
        embed.add_field(name='Top Role:', value=f'{membro.top_role.mention} ({membro.top_role.id})\n**Cor:** {membro.top_role.color}\n**Permissões:** [{membro.top_role.permissions.value}](https://finitereality.github.io/permissions-calculator/?v={membro.top_role.permissions.value})', inline=False)

        roles = [c for c in membro.roles if not c.name == '@everyone']
        roles = sorted(roles, key=lambda m: m.position, reverse=True)
        roles = [c.mention for c in roles]
        embed.add_field(name=f'Cargos: [{len(roles)}]', value=', '.join(roles), inline=False)
        with open(f"translation/perms_{self.bot.lang}.json", encoding='utf-8') as f:
            prms = json.load(f)
        perms = [prms[c[0]].capitalize() for c in membro.permissions_in(ctx.channel) if c[1]]
        embed.add_field(name=f'Este membro tem as seguintes permissões:', value=', '.join(perms), inline=False)

        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Disco(bot))