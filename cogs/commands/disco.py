import discord
from typing import Optional
from json import load
from assets.models.menus import baseMenu
from assets.packages import discordMenus as menus
from discord.ext import commands 

class OldMembersMenu(baseMenu):
    def __init__(self, pages, title, msg, author_page):
        super().__init__(pages, title, msg, '')
        self.author_page = author_page

    @property 
    async def embed(self):
        msg = self._msg
        msg += self.pages[self._index]
        embed = await self.bot.embed(self.ctx)
        embed.title = self._title.format(page=str(self._index+1), pages=str(len(self.pages)))
        embed.description = msg
        return embed

    @menus.button('👨')
    async def ath_page(self, _):
        self._index = self.author_page
        await self.message.edit(embed=await self.embed)

class Disco(commands.Cog, name='_disco_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, membro:discord.Member=None):
        trn = await ctx.trn
        member = membro or ctx.author 
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"].format(member_name=member.name)
        if not membro:
            embed.description = trn["emb_author"].format(author_mention=member.mention)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.guild_only() # Guild only pq não to com saco de adaptar pro privado.
    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, *, membro:discord.Member=None):
        trn = await ctx.trn
        membro = membro or ctx.author
        cor = membro.color if str(membro.color) != '#000000' else self.bot.color

        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"].format(member_name=membro.name)
        embed.color = cor

        embed.set_author(name=f'Userinfo | {membro.name}', icon_url=membro.avatar_url)

        bot = '**Bot**' if membro.bot else ''
        nick = f'\n{trn["nick"]} {membro.nick}' if membro.nick else ''
        embed.add_field(name=trn["emb_member"], value=f'**Tag:** {membro}{nick}\n**ID:** {membro.id}\n{bot}', inline=False)

        status = str(self.bot.emotes[f"sora_{str(membro.status)}"]) + f" {':iphone:' if membro.is_on_mobile() else ''} **{trn['status_l'][str(membro.status)]}**"
        
        if membro.activity:
            activity = trn["activities_l"]
            if membro.activity.type.value == 1:
                status += f'\n**{activity[membro.activity.type.value]}** [{membro.activity.name}]({membro.activity.url})'
            else:
                status += f'\n**{activity[membro.activity.type.value]}** {str(membro.activity.emoji).replace("None", "")}{str(membro.activity.name).replace("None", "")}'
        
        embed.add_field(name='Status:', value=status, inline=False)
        with open(f'translation/{await ctx.lang}/commands.json', encoding='utf-8') as lng:
            time_lang = load(lng)["_time"]
        embed.add_field(name=trn["emb_date"], value=trn["date_value"].format(
            created_at=membro.created_at.strftime("%d/%m/%Y %H:%M"), 
            joined_at=membro.joined_at.strftime("%d/%m/%Y %H:%M"), 
            rel_created=self.bot.getTime(time_lang, membro.created_at)[0].replace(", ", "").replace("e ", "").replace("and ", ""), 
            rel_joined=self.bot.getTime(time_lang, membro.joined_at)[0].replace(", ", "").replace("e ", "").replace("and ", "")),
            inline=False)

        embed.add_field(name='Top Role:', value=trn["topr_value"].format(member=membro), inline=False)

        roles = [c for c in membro.roles if not c.name == '@everyone']
        roles = sorted(roles, key=lambda m: m.position, reverse=True)
        roles = [c.mention for c in roles]

        if roles:
            embed.add_field(name=trn["emb_roles"].format(roles=len(roles)), value=', '.join(roles), inline=False)
        
        lang = await ctx.lang
        with open(f"translation/{lang}/perms.json", encoding='utf-8') as f:
            prms = load(f)
        perms = [prms[c[0]].capitalize() for c in membro.permissions_in(ctx.channel) if c[1]]
        embed.add_field(name=trn["emb_perms"], value=', '.join(perms), inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def oldmembers(self, ctx, param=None):
        trn = await ctx.trn
        membros = [(member, member.joined_at.timestamp()) for member in ctx.guild.members]
        membros.sort(key=lambda t: t[1])
        membros = [c[0] for c in membros]
        
        pages = []
        
        text = ""
        index = 0

        for k, membro in enumerate(membros):
            index += 1
            you = ''
            if membro == ctx.author:
                you = trn['_you']
                author_page = len(pages)
            text += f'`{k+1}º` {self.bot.emotes[f"sora_{membro.status}"]} `{membro}` {you}\n'
            if index == 10:
                pages.append(text)
                index = 0
                text = ""
            if k+1 == len(membros):
                pages.append(text)

        menu = OldMembersMenu(pages, trn["title"], trn["msg"], author_page)
        await menu.start(ctx)

def setup(bot):
    bot.add_cog(Disco(bot))
