import discord
import typing
from json import loads
import validators
import re
from asyncio import sleep
from inspect import Parameter
from datetime import datetime
from discord.ext import commands

class ServerAdmin(commands.Cog, name='_mod_cog'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not isinstance(ctx.channel, discord.TextChannel):
            raise commands.NoPrivateMessage
        return True

    @commands.command(aliases=['limpar'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, membro:typing.Optional[discord.Member], quantidade:typing.Optional[int]=100):
        trn = await ctx.trn
        if quantidade not in range(2, 501): # Out Range (or)
            high_low = trn["high_low"][quantidade<2]
            embed = await self.bot.erEmbed(ctx, trn["err_or_title"])
            embed.description = trn["err_or_desc"].format(high_low=high_low)
            return await ctx.send(embed=embed)

        loading = await self.bot.embed(ctx, invisible=True)
        loading.title = trn['deleting']
        msg = await ctx.send(embed=loading)
        msg_ids = [msg.id, ctx.message.id]
        check = lambda m: m.id not in msg_ids

        if membro:
            check = lambda m: m.author == membro and not m.id in msg_ids

        prg = await ctx.channel.purge(limit=quantidade+2, check=check)
        embed = await self.bot.embed(ctx)
        embed.title = trn['emb_title']
        embed.description = trn["emb_desc"].format(len_deleted=len(prg), of_member=f'{trn["of"] if membro else ""}{membro.mention if membro else ""}')
        await msg.edit(embed=embed, delete_after=15)
        await sleep(10)
        try:
            await msg.delete()
        except:
            pass
        await ctx.message.delete()

    @commands.command(aliases=['banir'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, membro:typing.Union[discord.Member, str], *, reason="_no_reason"):
        trn = await ctx.trn
        reason = trn.get(reason, reason)
        async def ban_embed(member):
            embed = await self.bot.embed(ctx)
            embed.title = trn["emb_title"].format(emote=self.bot.emotes["sora_ban"])
            embed.add_field(name=trn["emb_user"], value=trn["user_value"].format(member=str(member), member_id=member.id), inline=False)
            embed.add_field(name=trn["emb_staff"], value=trn["staff_value"].format(staff_mention=ctx.author.mention, role=ctx.author.top_role.name), inline=False)
            embed.add_field(name=trn["emb_reason"], value=reason, inline=False)
            embed.set_footer(text=trn["emb_footer"].format(member_name=member.name), icon_url=member.avatar_url)
            return embed

        if isinstance(membro, discord.Member):
            erro = await self.bot.erEmbed(ctx, trn['err_np_title'])

            if membro == ctx.author:
                erro.description = trn['np_selfban'].format(member_name=membro.name)

            elif membro == ctx.me:
                erro.description = trn['np_botban'].format(member_name=membro.name)

            elif (membro.top_role.position >= ctx.author.top_role.position and not ctx.author == ctx.guild.owner) or membro == ctx.guild.owner:
                erro.description = trn['np_ath_lower'].format(member_name=membro.name)

            elif membro.top_role.position >= ctx.me.top_role.position:
                erro.description = trn['np_bot_lower'].format(member_name=membro.name)

            if not isinstance(erro.description, type(discord.Embed.Empty)):
                return await ctx.send(embed=erro)

            await membro.ban(reason=trn['ban_reason'].format(author=str(ctx.author), reason=reason))

            embed = await ban_embed(membro)

            return await ctx.send(embed=embed)

        else:
            if not membro.isdigit():
                embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
                embed.description = trn["invalid_desc"]
                return await ctx.send(embed=embed)

            member = discord.Object(id=membro)

            loading = await self.bot.embed(ctx, invisible=True)
            loading.description = trn["banning"]
            m = await ctx.send(embed=loading)

            try:
                await ctx.guild.ban(member, reason=trn['ban_reason'].format(author=str(ctx.author), reason=reason))
            except discord.NotFound:
                embed = await self.bot.erEmbed(ctx, trn["err_notfound"])
                embed.description = trn["notfound_value"].format(id=member.id)
                return await m.edit(embed=embed)

            loading.description = trn["member_banned"]
            await m.edit(embed=loading)

            member = await self.bot.fetch_user(member.id)
            embed = await ban_embed(member)

            await m.edit(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, membro:discord.Member, *, reason="_no_reason"):
        trn = await ctx.trn
        ctx.command = self.bot.get_command('ban') # Perigoso, util para tradução
        reason = trn.get(reason, reason)

        erro = await self.bot.erEmbed(ctx, trn['err_np_title'])

        if membro == ctx.author:
            erro.description = trn['np_selfban']

        if membro == ctx.me:
            erro.description = trn['np_botban']

        if membro.top_role.position >= ctx.author.top_role.position:
            erro.description = trn['np_ath_lower'].format(member_name=membro.name)

        if membro.top_role.position >= ctx.me.top_role.position:
            erro.description= trn['np_bot_lower'].format(member_name=membro.name)

        if not isinstance(erro.description, type(discord.Embed.Empty)):
            return await ctx.send(embed=erro)

        await membro.ban(reason=trn['ban_reason'].format(author=ctx.author, reason=reason))
        await membro.unban(reason=trn['ban_reason'].format(author=ctx.author, reason=reason))
        
        embed = await self.bot.embed(ctx)
        embed.title = trn['emb_title'].replace('ban', 'soft-ban').format(emote=self.bot.emotes['sora_ban'])
        embed.add_field(name=trn['emb_user'], value=trn['user_value'].format(member=str(membro), member_id=str(membro.id)), inline=False)
        embed.add_field(name=trn['emb_staff'], value=trn['staff_value'].format(staff_mention=ctx.author.mention, role=ctx.author.top_role.name), inline=False)
        embed.add_field(name=trn['emb_reason'], value=reason, inline=False)
        embed.set_footer(text=trn['emb_footer'].format(member_name=membro.name), icon_url=membro.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['kickar'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, membro:discord.Member, *, reason="_no_reason"):
        trn = await ctx.trn
        erro = await self.bot.erEmbed(ctx, trn["err_np_title"])
        reason = trn.get(reason, reason)

        if membro == ctx.author:
            erro.description = trn['np_selfkick']

        elif membro == ctx.me:
            erro.description = trn['np_botkick']

        elif (membro.top_role.position >= ctx.author.top_role.position and not ctx.author == ctx.guild.owner) or membro == ctx.guild.owner:
            erro.description = trn['np_ath_lower'].format(member_name=membro.name)

        elif membro.top_role.position >= ctx.me.top_role.position:
            erro.description = trn['np_bot_lower'].format(member_name=membro.name)

        if not isinstance(erro.description, type(discord.Embed.Empty)):
            return await ctx.send(embed=erro)

        await membro.kick(reason=trn['kick_reason'].format(author=str(ctx.author), reason=reason))

        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"].format(emote=self.bot.emotes['sora_ban'])
        embed.description = trn["emb_desc"].format(member=membro, reason=reason)
        return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx):
        trn = await ctx.trn
        rms = None
        unlock = False
        try:
            rms = ctx.channel.overwrites[ctx.guild.default_role].read_messages # Manter permissão de ler mensagens
            if ctx.channel.overwrites[ctx.guild.default_role].send_messages == False:
                unlock = None
        except KeyError:
            rms = None

        await ctx.channel.set_permissions(ctx.guild.default_role, reason=trn["reason"].format(author=str(ctx.author)), send_messages=unlock, read_messages=rms)

        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"]
        embed.description = trn["emb_desc"].format(un=trn["_un"] if unlock is None else "", role=ctx.guild.default_role.name)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def allow(self, ctx, membro:discord.Member):
        trn = await ctx.trn
        no = ""
        allow = True
        erro = await self.bot.erEmbed(ctx)
        try:
            if membro in ctx.channel.members:
                # Caso ele possa ver o canal, vai mudar para não ver
                if ctx.channel.overwrites[membro].read_messages == True:
                    no = trn["_no"]
                    allow = None
        # Se deu KeyError é pq ele pode ver o canal, mas não tem overwrite (tem perm de cargo)
        except KeyError:
            erro.description = trn["err_perm"]
            return await ctx.send(embed=erro)

        # Caso for para tirar as permissões
        if no:
            await ctx.channel.set_permissions(membro, reason=trn["reason"].format(author=ctx.author), overwrite=None)
            if membro in ctx.channel.members:
                erro.description = trn["err_perm"]
                return await ctx.send(embed=erro)

        # Adicionar
        else:
            await ctx.channel.set_permissions(membro, reason=trn["reason"], send_messages=allow, read_messages=allow)
        
        embed = await self.bot.embed(ctx)
        embed.title = trn["emb_title"]
        embed.description = trn["emb_desc"].format(member_mention=membro.mention, no=no)
        await ctx.send(embed=embed)

    # Nem veja esse comando, ele é muito mal programado / dificil de entender.
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, json=None):
        trn = await ctx.trn
        json = json if json else {}
        # Caso seja maior que 2000 caracteres
        if not json:
            if ctx.message.attachments:
                if ctx.message.attachments[0].url.endswith(".txt"):
                    json = await self.bot.session.get(ctx.message.attachments[0].url)
                    json = await json.read()
                    json = json.decode('utf-8')
            else: # Caso não tenha nada
                raise commands.MissingRequiredArgument(Parameter(name="json", kind=Parameter.POSITIONAL_OR_KEYWORD))
        try:
            jsn = loads(json)
        except Exception as e:
            embed = await self.bot.erEmbed(ctx)
            embed.description = trn["err_invalid"]
            return await ctx.send(embed=embed)
        msg = jsn.get('content', None)

        invalid = []
        class EmbError(Exception):
            pass

        try:
            jsn_emb = jsn['embed']
        except:
            error = await self.bot.erEmbed(ctx)
            error.description = trn["err_noemb"]
            return await ctx.send(embed=error)
    
        # Daqui pra baixo, ele vai verificar tudo que é possivel no embed, e retirar do dicionario caso esteja errado
        # Todos esses invalid.append é pra mostrar oq está errado

        if jsn_emb.get("color"):
            try:
                jsn_emb["color"] = int(jsn_emb["color"])
            except ValueError:
                del(jsn_emb["color"])
                invalid.append("embed.color")

        if jsn_emb.get("title"):
            try:
                jsn_emb["title"] = jsn_emb["title"][:256]
            except:
                del(jsn_emb["title"])
                invalid.append("embed.title")

        if jsn_emb.get("description"):
            try:
                jsn_emb["description"] = jsn_emb["description"][:1024]
            except:
                del(jsn_emb["description"])
                invalid.append("embed.description")

        if jsn_emb.get('timestamp'):
            try:
                datetime.strptime(jsn_emb["timestamp"][:-4], "%Y-%m-%dT%H:%M:%S")
            except:
                del(jsn_emb["timestamp"])
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
                del(jsn_emb["thumbnail"])
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
                        del(jsn_emb["author"]["icon_url"])
                        invalid.append('embed.author.icon_url')
                    else:
                        pass
        except EmbError:
            pass

        for p, field in enumerate(jsn_emb.get('fields', [])):
            if not 'name' in field or not 'value' in field:
                del(jsn_emb["fields"][p])
                invalid.append(f'embed.fields[{p}]')
                continue

        try:
            await ctx.send(embed=discord.Embed.from_dict(jsn_emb), content=msg)
        except Exception as e:
            error = True # Isso pq alguns valores do field, não sei arrumar.
            await ctx.send(trn["err_fail"].format(error=e))
        
        if invalid:
            await ctx.send(trn["invalid"].format(invalids="; ".join(invalid), delete_after=10))

    @commands.command(aliases=['votar'])
    @commands.has_permissions(manage_messages=True)
    async def vote(self, ctx, canal:typing.Optional[discord.TextChannel], mensagem):
        trn = await ctx.trn
        canal = canal if canal else ctx.channel
        try:
            await ctx.message.delete()
        except:
            pass

        mentions = re.findall('<@(!|&)?([0-9]*)>', mensagem)
        mentions = [c for c in mentions if c]

        embed = await self.bot.embed(ctx)
        embed.title = trn["title"]
        embed.description = mensagem
        if mentions:
            mentions = [f'<@{c[0]}{c[1]}>' for c in mentions]

        if '@everyone' in mensagem:
            mentions.append('@everyone')

        msg = await canal.send(embed=embed, content=' '.join(mentions))
        if canal != ctx.channel:
            embed = await self.bot.embed(ctx, invisible=True)
            embed.description = trn["sended"].format(channel_mention=canal.mention, msg_link=msg.jump_url)
            await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❎')

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            trn = await ctx.trn
            _guild = await self.bot.db.get_guild(ctx.guild.id)

            embed = await self.bot.embed(ctx)
            embed.set_author(name=trn['emb_title'].format(guild_name=ctx.guild.name), icon_url=ctx.guild.icon_url)


            embed.add_field(name=trn['emb_lang'].format(lang=_guild["lang"]), value=trn['lang_value'])


            prx_em = self.bot.emotes['sora_on'] if _guild["prefix"] else self.bot.emotes['sora_off']
            embed.add_field(name=trn['emb_prefix'].format(emote=prx_em, prefix=str(_guild["prefix"]).replace("None", trn["none"])), value=trn['prefix_value'], inline=False)
            

            rep_em = self.bot.emotes['sora_off']
            rep_channel = trn['none']

            if not _guild.get("report"):
                pass
            else:
                rep_channel = ctx.guild.get_channel(_guild.get("report"))
                if not rep_channel:
                    await self.bot.db.update_guild({"_id": ctx.guild.id, "report": None})
                else:
                    rep_em = self.bot.emotes['sora_on']
                    rep_channel = f'#{rep_channel.name}'
            
            embed.add_field(name=trn['emb_report'].format(emote=rep_em, channel=rep_channel), value=trn['report_value'], inline=False)

            await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def lang(self, ctx, lang=None):
        trn = await ctx.trn
        with open("translation/languages.txt") as lng:
            langs = lng.read().split('\n')

        if not lang:
            embed = await self.bot.embed(ctx)
            embed.title = trn["emb_def_title"]
            langs = [f'`{c}`\n' for c in langs]
            embed.description = trn["emb_def_desc"].format(langs="".join(langs))
            return await ctx.send(embed=embed)

        if lang not in langs:
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            langs = [f'`{c}`\n' for c in langs]
            embed.description = trn["invalid_desc"].format(langs='\n'.join(langs))
            return await ctx.send(embed=embed)

        actual = ctx.lang
        if lang == actual:
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            embed.description = trn["actual_desc"]
            return await ctx.send(embed=embed)

        g = await self.bot.db.update_guild({'_id': ctx.guild.id, 'lang': lang.strip()})
        if g:
            embed = await self.bot.embed(ctx)
            embed.title = trn["emb_def_title"]
            embed.description = trn['emb_success'].format(lang=lang)

        else:
            embed = await self.bot.erEmbed(ctx)
            embed.description = trn['error']

        await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def prefix(self, ctx, prefix):
        trn = await ctx.trn
        _prefix = await ctx.guild_prefix
        prefix = prefix.lower()
        if prefix == _prefix: 
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            embed.description = trn['err_equal']
            return await ctx.send(embed=embed)
        if len(prefix) > 5 and not prefix == "reset":
            embed = await self.bot.erEmbed(ctx, trn["err_invalid"])
            embed.description = trn['err_five']
            return await ctx.send(embed=embed)
        if prefix == "reset":
            prefix = None
        g = await self.bot.db.update_guild({"_id": ctx.guild.id, "prefix": prefix})
        if g:
            embed = await self.bot.embed(ctx)
            embed.title = trn['emb_success']
            if prefix == None:
                prefix = trn['none']
            embed.description = trn['emb_prefix'].format(prefix = prefix)
            return await ctx.send(embed=embed)
        else:
            embed = await self.bot.erEmbed(ctx)
            embed.description = trn['error']
            return await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def reports(self, ctx, channel):
        trn = await ctx.trn
        _guild = await self.bot.db.get_guild(ctx.guild.id)
        
        if channel == "reset":
            if _guild.get('report'):
                await self.bot.db.update_guild({"_id": ctx.guild.id, "report": None})
            embed = await self.bot.embed(ctx)
            embed.title = trn['emb_disabled']
            embed.description = trn['disabled_desc']
            return await ctx.send(embed=embed)

        _channel = await commands.TextChannelConverter().convert(ctx, channel)
        
        if not _channel:
            embed = await self.bot.erEmbed(ctx, trn['err_notfound'])
            return await ctx.send(embed=embed)

        if _channel.id == _guild.get("report"):
            embed = await self.bot.erEmbed(ctx, trn['err_invalid'])
            embed.description = trn['err_equal']
            return await ctx.send(embed=embed)

        try:
            m = await _channel.send('.')
            await m.delete()
        except discord.HTTPException:
            embed = await self.bot.erEmbed(ctx, trn['err_invalid'])
            embed.description = trn['err_forbidden']
            return await ctx.send(embed=embed)

        await self.bot.db.update_guild({"_id": ctx.guild.id, "report": _channel.id})

        embed = await self.bot.embed(ctx)
        embed.description = trn['emb_title'].format(channel=_channel.mention)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerAdmin(bot))
