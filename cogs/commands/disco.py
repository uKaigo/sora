from re import search
import discord
from discord.ext import commands 
from utils import menus
from utils.custom import baseMenu, Embed

class OldMembersMenu(baseMenu):
    def __init__(self, pages, title, msg, author_page):
        super().__init__(pages, title, msg)
        self.author_page = author_page

    @property 
    def embed(self):
        msg = self._msg
        msg += self.pages[self._index]
        embed = Embed(self.ctx, description=msg)
        embed.title = self._title.format(page=str(self._index+1), pages=str(len(self.pages)))
        return embed

    @menus.button('👨')
    async def ath_page(self, _):
        if self._index != self.author_page: # pylint: disable=access-member-before-definition
            self._index = self.author_page
            await self.message.edit(embed=self.embed)

class Disco(commands.Cog, name='_disco_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, membro:discord.Member=None):
        member = membro or ctx.author 
        embed = Embed(ctx, title=ctx.t('emb_title', member_name=member.name))
        if not membro:
            embed.description = ctx.t('emb_author', author_mention=member.mention)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.guild_only() # Guild only pq não to com saco de adaptar pro privado.
    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, *, membro:discord.Member=None):
        lang = ctx.lang
        membro = membro or ctx.author
        cor = membro.color if str(membro.color) != '#000000' else self.bot.color

        flags_emote = set()
        for flag in membro.public_flags.all():
            flags_emote.add(str(self.bot.emotes.get(flag.name, '')))
        flags_emote = " ".join(flags_emote)

        embed = Embed(ctx, title=f'{flags_emote} {membro}', color=cor)

        embed.set_thumbnail(url=membro.avatar_url)

        bot = '**Bot**' if membro.bot else ''
        nick = f'\n{ctx.t("nick")} {membro.nick}' if membro.nick else ''
        embed.add_field(name=ctx.t('emb_member'), value=f'**Tag:** {membro}{nick}\n**ID:** {membro.id}\n{bot}', inline=False)

        status = str(self.bot.emotes[f'sora_{str(membro.status)}']) + f" {':iphone:' if membro.is_on_mobile() else ''} **{ctx.t('status_l.' + str(membro.status))}**"
        
        if membro.activity:
            status += f"\n**{ctx.t(f'activities_l.{membro.activity.type.value}')}** "
            if membro.activity.type.value == 1:
                status += f'[{membro.activity.name}]({membro.activity.url})'
            elif hasattr(membro.activity, 'emoji'):
                status += f'{str(membro.activity.emoji).replace("None", "")}{str(membro.activity.name).replace("None", "")}'
            else:
                status += f'{str(membro.activity.name)}'

        embed.add_field(name='Status:', value=status, inline=False)
        embed.add_field(name=ctx.t('emb_date'), value=ctx.t('date_value',
            created_at=membro.created_at.strftime('%d/%m/%Y %H:%M'), 
            joined_at=membro.joined_at.strftime('%d/%m/%Y %H:%M'), 
            rel_created=search(r'\d+ \w+', self.bot.getTime(ctx.t('_time', _nc=1), membro.created_at))[0], 
            rel_joined=search(r'\d+ \w+', self.bot.getTime(ctx.t('_time', _nc=1), membro.joined_at))[0]),
            inline=False)

        embed.add_field(name='Top Role:', value=ctx.t('topr_value', member=membro), inline=False)

        roles = [c for c in membro.roles if not c.name == '@everyone']
        roles = sorted(roles, key=lambda m: m.position, reverse=True)
        roles = [c.mention for c in roles]

        if roles:
            embed.add_field(name=ctx.t('emb_roles', roles=len(roles)), value=', '.join(roles), inline=False)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def oldmembers(self, ctx):
        members = [(member, member.joined_at.timestamp()) for member in ctx.guild.members]
        members.sort(key=lambda t: t[1])
        members = [c[0] for c in members]
        
        pages = []
        
        text = ""
        index = 0

        for k, member in enumerate(members):
            index += 1
            you = ''
            if member == ctx.author:
                you = ctx.t('_you')
                author_page = len(pages)
            text += f'`{k+1}º` {self.bot.emotes[f"sora_{member.status}"]} `{member}` {you}\n'
            if index == 10:
                pages.append(text)
                index = 0
                text = ""
            if k+1 == len(members):
                pages.append(text)

        menu = OldMembersMenu(pages, ctx.t('title'), ctx.t('msg'), author_page)
        await menu.start(ctx)

def setup(bot):
    bot.add_cog(Disco(bot))
