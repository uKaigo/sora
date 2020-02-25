import discord
import typing
import json
import assets.discordMenus as menus
from discord.ext import commands 

class OldMembersMenu(menus.Menu):
    def __init__(self, pages, msg):
        super().__init__(clear_reactions_after=True, timeout=30)
        self.index = 0
        self.pages = [c for c in pages if c]
        self.msg = msg
        self.nopage = False

    def should_add_reactions(self):
        if self.nopage:
            return 0
        return len(self.buttons)

    async def send_initial_message(self, ctx, channel):
        msg = self.msg
        msg += self.pages[self.index]
        embed = self.bot.embed(self.ctx)
        embed.title = f'Old Members | Página {self.index+1}/{len(self.pages)}'
        embed.description = msg
        if len(self.pages) == 1:
            self.nopage = True
        return await ctx.send(embed=embed)

    @menus.button('⬅️')
    async def voltar(self, payload):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.pages)-1
        msg = self.msg
        msg += self.pages[self.index]
        embed = self.bot.embed(self.ctx)
        embed.title = f'Old Members | Página {self.index+1}/{len(self.pages)}'
        embed.description = msg
        await self.message.edit(embed=embed)    

    @menus.button('➡️')
    async def avancar(self, payload):
        self.index += 1
        msg = self.msg
        try:
            msg += self.pages[self.index]
        except:
            self.index = 0
            msg += self.pages[self.index]
        embed = self.bot.embed(self.ctx)
        embed.title = f'Old Members | Página {self.index+1}/{len(self.pages)}'
        embed.description = msg
        await self.message.edit(embed=embed)
        
    @menus.button('❌')
    async def parar(self, _):
        self.stop()

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

    @commands.guild_only() # Guild only pq não to com saco de adaptar pro privado.
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
                status += f'\n**{activity[membro.activity.type.value]}** {str(membro.activity.emoji).replace("None", "")}{str(membro.activity.name).replace("None", "")}'
        embed.add_field(name='Status:', value=status, inline=False)
        
        embed.add_field(name='Data:', value=f'**Que criou a conta:** {membro.created_at.strftime("%d/%m/%Y %H:%M")} ({self.bot.getTime(membro.created_at)[0].replace(", ", "").replace("e ", "")} atrás)\n**Que entrou no server:** {membro.joined_at.strftime("%d/%m/%Y %H:%M")} ({self.bot.getTime(membro.joined_at)[0].replace(", ", "").replace("e ", "")} atrás)', inline=False)
        
        embed.add_field(name='Top Role:', value=f'{membro.top_role.mention} ({membro.top_role.id})\n**Cor:** {membro.top_role.color}\n**Permissões:** [{membro.top_role.permissions.value}](https://finitereality.github.io/permissions-calculator/?v={membro.top_role.permissions.value})', inline=False)

        roles = [c for c in membro.roles if not c.name == '@everyone']
        roles = sorted(roles, key=lambda m: m.position, reverse=True)
        roles = [c.mention for c in roles]
        cargos = roles if roles else ["Nenhum."]
        embed.add_field(name=f'Cargos: [{len(roles) if roles else "0"}]', value=', '.join(cargos), inline=False)
        with open(f"translation/perms_{self.bot.lang}.json", encoding='utf-8') as f:
            prms = json.load(f)
        perms = [prms[c[0]].capitalize() for c in membro.permissions_in(ctx.channel) if c[1]]
        embed.add_field(name=f'Este membro tem as seguintes permissões:', value=', '.join(perms), inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(usage='{}oldmembers', description='Exibe os membros mais antigos do servidor.\nUse `-bots` depois do comando para não incluir bots.')
    async def oldmembers(self, ctx, param=None):
        nao = ""
        if param == '-bots':
            nao = " não"
            membros = [(member, member.joined_at.timestamp()) for member in ctx.guild.members if not member.bot]
        else:
            membros = [(member, member.joined_at.timestamp()) for member in ctx.guild.members]
        
        membros.sort(key=lambda t: t[1])
        membros = [c[0] for c in membros]
        
        pages = []
        
        text = ""
        index = 0

        for k, membro in enumerate(membros):
            index += 1
            text += f'`{k+1}º` {self.bot.emotes[f"sora_{membro.status}"]} `{membro}`\n'
            if index == 10:
                pages.append(text)
                index = 0
                text = ""
            if k+1 == len(membros):
                pages.append(text)

        msg = f"Estes são os membros mais antigos do servidor.\nBots{nao} exibidos.\n\n"
        menu = OldMembersMenu(pages, msg)
        await menu.start(ctx)

def setup(bot):
    bot.add_cog(Disco(bot))
