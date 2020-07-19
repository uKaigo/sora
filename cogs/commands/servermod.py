from asyncio import sleep
from inspect import Parameter
from datetime import datetime
from json import loads
import typing
import re
import validators
import discord
from discord.ext import commands
from utils.custom import Embed
from utils.converters import EmojiConverter, UserConverter

def can_modify(ctx, member):
    if ctx.author == ctx.guild.owner:
        return 0
    if member == ctx.author:
        return 1
    if member == ctx.me:
        return 2
    if member.top_role.position >= ctx.author.top_role.position \
            or member == ctx.guild.owner:
        return 3
    if member.top_role.position >= ctx.me.top_role.position \
            or member == ctx.guild.owner:
        return 4 
    return 0

class ServerAdmin(commands.Cog, name='_mod_cog'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not isinstance(ctx.channel, discord.TextChannel):
            raise commands.NoPrivateMessage
        return True

    @commands.group(aliases=['limpar'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, membro:typing.Optional[discord.Member], quantidade:typing.Optional[int]=100):
        if ctx.invoked_subcommand is not None:
            return 
        if quantidade not in range(2, 501): # Out Range (or)
            high_low = ctx.t(f'high_low.{int(quantidade<2)}')
            embed = Embed(
                ctx, 
                title=ctx.t('err_or_title'), 
                description=ctx.t('err_or_desc', high_low=high_low), 
                error=True)
            return await ctx.send(embed=embed)

        loading = Embed(ctx, title=ctx.t('deleting'), color=self.bot.neutral)
        msg = await ctx.send(embed=loading)
        msg_ids = [msg.id, ctx.message.id]
        
        check = lambda m: m.id not in msg_ids

        if membro:
            check = lambda m: m.author == membro and not m.id in msg_ids

        prg = await ctx.channel.purge(limit=quantidade+2, check=check)
       
        embed = Embed(ctx, title=ctx.t('emb_title'))
        embed.description = ctx.t(
            'emb_desc', 
            len_deleted=len(prg), 
            of_member=f'{ctx.t("of") if membro else ""}{membro.mention if membro else ""}'
        )
        
        await msg.edit(embed=embed)
        await sleep(10)
        try:
            await msg.delete()
            await ctx.message.delete()
        except:
            pass

    @clear.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def match(self, ctx, pattern, limit:int=100):
        if limit not in range(2, 501): # Out Range (or)
            high_low = ctx.t(f'high_low.{int(limit<2)}')
            embed = Embed(
                ctx, 
                title=ctx.t('err_or_title'), 
                description=ctx.t('err_or_desc', high_low=high_low),
                error=True
            )
            return await ctx.send(embed=embed)
    
        loading = Embed(ctx, title=ctx.t('deleting'), color=self.bot.neutral)

        msg = await ctx.send(embed=loading)
        msg_ids = [msg.id, ctx.message.id]

        check = lambda m: re.search(pattern, m.content) != None and m.id not in msg_ids 

        prg = await ctx.channel.purge(limit=limit+2, check=check)

        embed = Embed(ctx, title=ctx.t('emb_title'))
        embed.description = ctx.t('emb_desc', len_deleted=len(prg), pattern=pattern)
        await msg.edit(embed=embed)
        await sleep(10)
        
        try:
            await msg.delete()
            await ctx.message.delete()
        except:
            pass

    @commands.command(aliases=['banir'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, membro:UserConverter, *, reason='_no_reason'):
        reason = ctx.t(reason)
        def ban_embed(member):
            embed = Embed(
                ctx, 
                title=ctx.t('emb_title', emote=self.bot.emotes['sora_ban'])
            )
            embed.add_field(name=ctx.t('emb_user'), value=ctx.t('user_value', member=str(member), member_id=member.id), inline=False)
            embed.add_field(name=ctx.t('emb_staff'), value=ctx.t('staff_value', staff_mention=ctx.author.mention, role=ctx.author.top_role.name), inline=False)
            embed.add_field(name=ctx.t('emb_reason'), value=reason, inline=False)
            embed.set_footer(text=ctx.t('emb_footer', member_name=member.name), icon_url=member.avatar_url)
            return embed

        error = self.bot.erEmbed(ctx, ctx.t('err_np_title'))

        mdf_state = can_modify(ctx, membro)
        if mdf_state != 0:
            error.description = ctx.t(f'cant_ban.{mdf_state-1}')

        if not isinstance(error.description, type(discord.Embed.Empty)):
            return await ctx.send(embed=error)

        await ctx.guild.ban(membro, reason=ctx.t('ban_reason', author=str(ctx.author), reason=reason))

        embed = ban_embed(membro)

        return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, membro:discord.Member, *, reason='_no_reason'):
        ctx.command = self.bot.get_command('ban') # Perigoso, util para tradução
        reason = ctx.t(reason)

        error = self.bot.erEmbed(ctx, ctx.t('err_np_title'))

        mdf_state = can_modify(ctx, membro)
        if mdf_state != 0:
            error.description = ctx.t(f'cant_ban.{mdf_state-1}')

        if not isinstance(error.description, type(discord.Embed.Empty)):
            return await ctx.send(embed=error)

        await membro.ban(reason=ctx.t('ban_reason', author=ctx.author, reason=reason))
        await membro.unban(reason=ctx.t('ban_reason', author=ctx.author, reason=reason))
        
        embed = self.bot.embed(ctx)
        embed.title = ctx.t('emb_title', emote=self.bot.emotes['sora_ban']).replace('ban', 'soft-ban')
        embed.add_field(name=ctx.t('emb_user'), value=ctx.t('user_value', member=str(membro), member_id=membro.id), inline=False)
        embed.add_field(name=ctx.t('emb_staff'), value=ctx.t('staff_value', staff_mention=ctx.author.mention, role=ctx.author.top_role.name), inline=False)
        embed.add_field(name=ctx.t('emb_reason'), value=reason, inline=False)
        embed.set_footer(text=ctx.t('emb_footer', member_name=membro.name), icon_url=membro.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['kickar'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, membro:discord.Member, *, reason='_no_reason'):
        erro = self.bot.erEmbed(ctx, ctx.t('err_np_title'))
        reason = ctx.t(reason)

        mdf_state = can_modify(ctx, membro)
        if mdf_state != 0:
            erro.description = ctx.t(f'cant_kick.{mdf_state-1}')

        if not isinstance(erro.description, type(discord.Embed.Empty)):
            return await ctx.send(embed=erro)

        await membro.kick(reason=ctx.t('kick_reason', author=str(ctx.author), reason=reason))

        embed = self.bot.embed(ctx)
        embed.title = ctx.t('emb_title', emote=self.bot.emotes['sora_ban'])
        embed.description = ctx.t('emb_desc', member=membro, reason=reason)
        return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx):
        rms = None
        unlock = False
        try:
            rms = ctx.channel.overwrites[ctx.guild.default_role].read_messages # Manter permissão de ler mensagens
            if ctx.channel.overwrites[ctx.guild.default_role].send_messages == False:
                unlock = None
        except KeyError:
            rms = None

        await ctx.channel.set_permissions(ctx.guild.default_role, reason=ctx.t('reason', author=ctx.author), send_messages=unlock, read_messages=rms)

        embed = self.bot.embed(ctx)
        embed.title = ctx.t('emb_title')
        embed.description = ctx.t('emb_desc', un=ctx.t('_un') if unlock is None else '', role=ctx.guild.default_role.name)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def allow(self, ctx, membro:discord.Member):
        no = ''
        allow = True
        erro = self.bot.erEmbed(ctx)
        try:
            if membro in ctx.channel.members:
                # Caso ele possa ver o canal, vai mudar para não ver
                if ctx.channel.overwrites[membro].read_messages == True:
                    no = ctx.t('_no')
                    allow = None
        # Se deu KeyError é pq ele pode ver o canal, mas não tem overwrite (tem perm de cargo)
        except KeyError:
            erro.description = ctx.t('err_perm')
            return await ctx.send(embed=erro)

        # Caso for para tirar as permissões
        if no:
            await ctx.channel.set_permissions(membro, reason=ctx.t('reason', author=ctx.author), overwrite=None)
            if membro in ctx.channel.members:
                erro.description = ctx.t('err_perm')
                return await ctx.send(embed=erro)

        # Adicionar
        else:
            await ctx.channel.set_permissions(membro, reason=ctx.t('reason'), send_messages=allow, read_messages=allow)
        
        embed = self.bot.embed(ctx)
        embed.title = ctx.t('emb_title')
        embed.description = ctx.t('emb_desc', member_mention=membro.mention, no=no)
        await ctx.send(embed=embed)

    # Nem veja esse comando, ele é muito mal programado / dificil de entender.
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, json=None):
        json = json if json else {}
        # Caso seja maior que 2000 caracteres
        if not json:
            if ctx.message.attachments:
                if ctx.message.attachments[0].url.endswith('.txt'):
                    json = await self.bot.session.get(ctx.message.attachments[0].url)
                    json = await json.read()
                    json = json.decode('utf-8')
            else: # Caso não tenha nada
                raise commands.MissingRequiredArgument(Parameter(name='json', kind=Parameter.POSITIONAL_OR_KEYWORD))
        try:
            jsn = loads(json)
        except Exception as e:
            embed = self.bot.erEmbed(ctx)
            embed.description = ctx.t('err_invalid')
            return await ctx.send(embed=embed)
        msg = jsn.get('content', None)

        invalid = []
        class EmbError(Exception):
            pass

        try:
            jsn_emb = jsn['embed']
        except:
            error = self.bot.erEmbed(ctx)
            error.description = ctx.t('err_noemb')
            return await ctx.send(embed=error)
    
        # Daqui pra baixo, ele vai verificar tudo que é possivel no embed, e retirar do dicionario caso esteja errado
        # Todos esses invalid.append é pra mostrar oq está errado

        if jsn_emb.get('color'):
            try:
                jsn_emb['color'] = int(jsn_emb['color'])
            except ValueError:
                del(jsn_emb['color'])
                invalid.append('embed.color')

        if jsn_emb.get('title'):
            try:
                jsn_emb['title'] = jsn_emb['title'][:256]
            except:
                del(jsn_emb['title'])
                invalid.append('embed.title')

        if jsn_emb.get('description'):
            try:
                jsn_emb['description'] = jsn_emb['description'][:1024]
            except:
                del(jsn_emb['description'])
                invalid.append('embed.description')

        if jsn_emb.get('timestamp'):
            try:
                datetime.strptime(jsn_emb['timestamp'][:-4], '%Y-%m-%dT%H:%M:%S')
            except:
                del(jsn_emb['timestamp'])
                invalid.append('embed.timestamp')

        if jsn_emb.get('footer'):
            if jsn_emb['footer'].get('icon_url'):
                if validators.url(jsn_emb['footer'].get('icon_url', 'G. A. G. A.')):
                    pass
                else:
                    del(jsn_emb['footer']['icon_url'])
                    invalid.append('embed.footer.icon_url')

        if jsn_emb.get('thumbnail'):
            if validators.url(jsn_emb['thumbnail'].get('url', 'G. A. G. A.')):
                pass
            else:
                del(jsn_emb['thumbnail'])
                invalid.append('embed.thumbnail')

        if jsn_emb.get('image'):
            if validators.url(jsn_emb['image'].get('url', 'G. A. G. A.')):
                pass
            else:
                del(jsn_emb['image'])
                invalid.append('embed.thumbnail')

        try: # Author      
            if jsn_emb.get('author'):
                if not jsn_emb['author'].get('name'):
                    del(jsn_emb['author'])
                    invalid.append('embed.author.name')
                    raise EmbError

                if jsn_emb['author'].get('url'):
                    if not validators.url(jsn_emb['author']['url']):
                        del(jsn_emb["author"]["url"])
                        invalid.append('embed.author.url')
                    else:
                        pass
                if jsn_emb['author'].get('icon_url'):
                    if not validators.url(jsn_emb['author']['icon_url']):
                        del(jsn_emb['author']['icon_url'])
                        invalid.append('embed.author.icon_url')
                    else:
                        pass
        except EmbError:
            pass

        for p, field in enumerate(jsn_emb.get('fields', [])):
            if not 'name' in field or not 'value' in field:
                del(jsn_emb['fields'][p])
                invalid.append(f'embed.fields[{p}]')
                continue

        try:
            await ctx.send(embed=discord.Embed.from_dict(jsn_emb), content=msg)
        except Exception as e:
            error = True # Isso pq alguns valores do field, não sei arrumar.
            await ctx.send(ctx.t('err_fail', error=e))
        
        if invalid:
            await ctx.send(ctx.t('invalid', invalids="; ".join(invalid), delete_after=10))

    @commands.command(aliases=['vote'])
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, emojis: commands.Greedy[EmojiConverter], channel:typing.Optional[discord.TextChannel], *, message):
        channel = channel if channel else ctx.channel

        # PartialEmojis não podem ser adicionados pelo bot, por isso essa verificaçao
        emojis = set(filter(lambda e: type(e) != discord.PartialEmoji, emojis))
        if not emojis:
            emojis = {'✅', '❎'}
        
        if len(emojis) == 1:
            emojis.add('❎')

        try:
            await ctx.message.delete()
        except:
            pass

        mentions = re.findall('<@(!|&)?([0-9]+)>', message)
        mentions = [c for c in mentions if c]

        embed = self.bot.embed(ctx)
        embed.title = ctx.t('title')
        embed.description = message.strip('\\ ')
        if mentions:
            mentions = [f'<@{c[0]}{c[1]}>' for c in mentions]

        if '@everyone' in message:
            mentions.append('@everyone')
        elif '@here' in message: # Everyone vale mais que o here, por isso o elif.
            mentions.append('@here')

        msg = await channel.send(embed=embed, content=' '.join(mentions))
        for emoji in emojis:
            try:
                await msg.add_reaction(emoji)
            except discord.HTTPException:
                pass

        if channel != ctx.channel:
            embed = self.bot.embed(ctx, invisible=True)
            embed.description = ctx.t('sended', channel_mention=channel.mention, msg_link=msg.jump_url)
            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            _guild = await self.bot.db.guilds.find(ctx.guild.id)

            embed = self.bot.embed(ctx)
            embed.set_author(name=ctx.t('emb_title', guild_name=ctx.guild.name), icon_url=ctx.guild.icon_url)


            embed.add_field(name=ctx.t('emb_lang', lang=_guild["lang"]), value=ctx.t('lang_value'))


            prx_em = self.bot.emotes['sora_on'] if _guild['prefix'] else self.bot.emotes['sora_off']
            embed.add_field(name=ctx.t('emb_prefix', emote=prx_em, prefix=str(_guild['prefix']).replace('None', ctx.t('none'))), value=ctx.t('prefix_value'), inline=False)
            

            rep_em = self.bot.emotes['sora_off']
            rep_channel = ctx.t('none')

            if not _guild.get('report'):
                pass
            else:
                rep_channel = ctx.guild.get_channel(_guild.get('report'))
                if not rep_channel:
                    await self.bot.db.guilds.update({'_id': ctx.guild.id, 'report': None})
                else:
                    rep_em = self.bot.emotes['sora_on']
                    rep_channel = f'#{rep_channel.name}'
            
            embed.add_field(name=ctx.t('emb_report', emote=rep_em, channel=rep_channel), value=ctx.t('report_value'), inline=False)

            await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def lang(self, ctx, lang=None):
        with open('translation/languages.txt') as lng:
            langs = lng.read().split('\n')

        if not lang:
            embed = self.bot.embed(ctx)
            embed.title = ctx.t('emb_def_title')
            langs = [f'`{c}`\n' for c in langs]
            embed.description = ctx.t('emb_def_desc', langs="".join(langs))
            return await ctx.send(embed=embed)

        if lang not in langs:
            embed = self.bot.erEmbed(ctx, ctx.t('err_invalid'))
            langs = [f'`{c}`\n' for c in langs]
            embed.description = ctx.t('invalid_desc', langs='\n'.join(langs))
            return await ctx.send(embed=embed)

        actual = ctx.lang
        if lang == actual:
            embed = self.bot.erEmbed(ctx, ctx.t('err_invalid'))
            embed.description = ctx.t('actual_desc')
            return await ctx.send(embed=embed)

        g = await self.bot.db.guilds.update({'_id': ctx.guild.id, 'lang': lang.strip()})
        embed = self.bot.embed(ctx)
        embed.title = ctx.t('emb_def_title')
        embed.description = ctx.t('emb_success', lang=lang)
        return await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def prefix(self, ctx, prefix):
        _prefix = await ctx.guild_prefix()
        if _prefix and prefix.lower() == _prefix.lower(): 
            embed = self.bot.erEmbed(ctx, ctx.t('err_invalid'))
            embed.description = ctx.t('err_equal')
            return await ctx.send(embed=embed)
        if len(prefix) > 5 and not prefix in ('reset', self.bot.config['prefix']):
            embed = self.bot.erEmbed(ctx, ctx.t('err_invalid'))
            embed.description = ctx.t('err_five')
            return await ctx.send(embed=embed)
        if prefix in ('reset', self.bot.config['prefix']):
            prefix = None
        
        await self.bot.db.guilds.update({'_id': ctx.guild.id, 'prefix': prefix}) 

        embed = self.bot.embed(ctx)
        embed.title = ctx.t('emb_success')
        if prefix == None:
            prefix = ctx.t('none')
        embed.description = ctx.t('emb_prefix', prefix = prefix)
        return await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def reports(self, ctx, channel):
        _guild = await self.bot.db.guilds.find(ctx.guild.id)
        
        if channel == 'reset':
            if _guild.get('report'):
                await self.bot.db.guilds.update({'_id': ctx.guild.id, 'report': None})
            embed = self.bot.embed(ctx)
            embed.title = ctx.t('emb_disabled')
            embed.description = ctx.t('disabled_desc')
            return await ctx.send(embed=embed)

        try:
            _channel = await commands.TextChannelConverter().convert(ctx, channel)
        except commands.BadArgument:
            embed = self.bot.erEmbed(ctx, ctx.t('err_notfound'))
            embed.description = ctx.t('notfound_desc', channel=channel)
            return await ctx.send(embed=embed)


        if not _channel:
            embed = self.bot.erEmbed(ctx, ctx.t('err_notfound'))
            return await ctx.send(embed=embed)

        if _channel.id == _guild.get('report'):
            embed = self.bot.erEmbed(ctx, ctx.t('err_invalid'))
            embed.description = ctx.t('err_equal')
            return await ctx.send(embed=embed)

        try:
            m = await _channel.send('.')
            await m.delete()
        except discord.HTTPException:
            embed = self.bot.erEmbed(ctx, ctx.t('err_invalid'))
            embed.description = ctx.t('err_forbidden')
            return await ctx.send(embed=embed)

        await self.bot.db.guilds.update({'_id': ctx.guild.id, 'report': _channel.id})

        embed = self.bot.embed(ctx)
        embed.description = ctx.t('emb_title', channel=_channel.mention)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerAdmin(bot))
