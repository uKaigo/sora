import discord
import typing
from json import loads 
import validators
import re
from inspect import Parameter
from datetime import datetime
from discord.ext import commands

class ServerAdmin(commands.Cog, name='Moderação'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not isinstance(ctx.channel, discord.TextChannel):
            raise commands.NoPrivateMessage
        return True


    @commands.command(usage='{}purge (membro) (2-500)', description='Limpa `x` mensagens de um canal ou de um membro. [Gerenciar Mensagens]', aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, membro:typing.Optional[discord.Member], quantidade:typing.Optional[int]=100):
        check = None
        if quantidade not in range(2, 501):
            npos = "alto" if quantidade > 500 else "baixo"
            embed = self.bot.erEmbed(ctx, 'Quantidade inválida.')
            embed.description = f'Você digitou um número muito {npos}, utilize apenas números entre 2 e 500'
            return await ctx.send(embed=embed)

        if membro:
            check = lambda m: m.author == membro

        await ctx.message.delete()

        prg = await ctx.channel.purge(limit=quantidade, check=check)
        embed = self.bot.embed(ctx)
        embed.title = '🧹 | Purge'
        embed.description = f'Foram deletadas {len(prg)} mensagens{" de " if membro else ""}{membro.mention if membro else ""}.'
        await ctx.send(embed=embed, delete_after=15)
        
    @commands.command(usage='{}ban [membro] (motivo)', description='Bane um membro que está no servidor (ou não). [Banir Membros]', aliases=['banir'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, membro:typing.Union[discord.Member, str], *, reason="Não informado."):
        if type(membro) == discord.Member:
            erro = self.bot.erEmbed(ctx, 'Sem permissão.')

            if membro == ctx.author:
                erro.description = 'Você não pode se banir, bobinho!'

            if membro == ctx.me:
                erro.description = 'Não posso me banir...'

            if membro.top_role.position >= ctx.author.top_role.position or membro == ctx.guild.owner:
                erro.description = f'Você não tem permissão para banir **{membro.name}** (seu cargo é menor ou igual que o dele)'

            if membro.top_role.position >= ctx.me.top_role.position:
                erro.description = f'Eu não tenho permissão para banir **{membro.name}** (cargo dele é maior ou igual que o meu)'

            if type(erro.description) != discord.Embed.Empty: # isinstance não funcionaria
                return await ctx.send(embed=erro)
            await membro.ban(reason=f'Por {ctx.author} || Motivo: {reason}')

            # Não vou usar o self.bot.embed, já que esse embed sobescreve tudo.
            embed = self.bot.embed(ctx)
            embed.title = f'{self.bot.emotes["sora_ban"]} | Ban'
            embed.description = 'Desrespeitou as regras, deu nisso aí.'
            embed.add_field(name=f'Usuário:', value=f'Tag: `{membro}`\nId: `{membro.id}`', inline=False)
            embed.add_field(name=f'Staffer:', value=f'Tag: `{ctx.author}`\nCargo: `{ctx.author.top_role.name}`', inline=False)
            embed.add_field(name=f'Motivo:', value=reason, inline=False)
            embed.set_footer(text=f'Banido: {membro.name}', icon_url=membro.avatar_url)
            return await ctx.send(embed=embed)

        else:
            try:
                int(membro)
            except ValueError:
                embed = self.bot.erEmbed(ctx, 'Inválido')
                embed.description = 'O "id" que você digitou não é um número!'
                return await ctx.send(embed=embed)

            member = discord.Object(id=membro)

            embed = self.bot.embed(ctx, invisible=True)
            embed.description = 'Banindo...'
            m = await ctx.send(embed=embed)

            try:
                await ctx.guild.ban(member, reason=f'Por {ctx.author} || Motivo: {reason}')
            except discord.NotFound:
                embed = self.bot.erEmbed(ctx, 'Id inválido')
                embed.description = f'O id que você digitou ({member.id}) não pertence à algum membro.\nVerifique erros de escrita.'
                return await m.edit(embed=embed)

            embed.description = 'Membro banido, carregando embed...'
            await m.edit(embed=embed)

            member = await self.bot.fetch_user(member.id)
            embed = self.bot.embed(ctx)
            embed.title = f'{self.bot.emotes["sora_ban"]} | Ban'
            embed.description = 'Desrespeitou as regras deu nisso ai.'
            embed.add_field(name=f'Usuário:', value=f'Tag: `{member}`\nId: `{member.id}`', inline=False)
            embed.add_field(name=f'Staffer:', value=f'Menção: {ctx.author.mention}\nCargo: `{ctx.author.top_role.name}`', inline=False)
            embed.add_field(name=f'Motivo:', value=reason)
            embed.set_footer(text=f'Banido: {member.name}', icon_url=member.avatar_url)

            await m.edit(embed=embed)

    @commands.command(usage='{}softban [membro] (motivo)', description='Bane e desbane um membro, util para limpar as mensagens rapidamente.')
    @commands.has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, membro:discord.Member, *, reason="Não informado."):
        erro = self.bot.erEmbed(ctx, 'Sem permissão.')

        if membro == ctx.author:
            erro.description = 'Você não pode se banir, bobinho!'

        if membro == ctx.me:
            erro.description = 'Não posso me banir...'

        if membro.top_role.position >= ctx.author.top_role.position:
            erro.description = f'Você não tem permissão para banir **{membro.name}** (seu cargo é menor ou igual que o dele)'

        if membro.top_role.position >= ctx.me.top_role.position:
            erro.description=f'Eu não tenho permissão para banir **{membro.name}** (cargo dele é maior ou igual que o meu)'

        if type(erro.description) != discord.Embed.Empty: # isinstance não funciona aqui
            return await ctx.send(embed=erro)

        await membro.ban(reason=f'Por {ctx.author} || Motivo: {reason}')
        await membro.unban(reason=f'Por {ctx.author} || Motivo: {reason}')
        
        embed = self.bot.embed(ctx)
        embed.title = f'{self.bot.emotes["sora_ban"]} | SoftBan'
        embed.description = 'Desrespeitou as regras, deu nisso aí.'
        embed.add_field(name=f'Usuário:', value=f'Tag: `{membro}`\nId: `{membro.id}`', inline=False)
        embed.add_field(name=f'Staffer:', value=f'Tag: `{ctx.author}`\nCargo: `{ctx.author.top_role.name}`', inline=False)
        embed.add_field(name=f'Motivo:', value=reason, inline=False)
        embed.set_footer(text=f'Punido: {membro.name}', icon_url=membro.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(usage='{}kick [membro] (motivo)', description='Expulsa um membro do servidor. [Expulsar Membros]')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, membro:discord.Member, *, reason="Não informado."):
        erro = self.bot.erEmbed(ctx, 'Sem permissão.')
        if membro.top_role.position >= ctx.author.top_role.position:
            erro.description = f'Você não tem permissão para expulsar **{membro.name}** (seu cargo é menor ou igual que o dele)'

        if membro.top_role.position >= ctx.me.top_role.position:
            erro.description = f'Eu não tenho permissão para expulsar **{membro.name}** (cargo dele é maior ou igual que o meu)'

        if not isinstance(erro.description, type(discord.Embed.Empty)):
            return await ctx.send(embed=erro)

        await membro.kick(reason=f'Por {ctx.author} || Motivo: {reason}')

        embed = self.bot.embed(ctx)
        embed.title = f'{self.bot.emotes["sora_ban"]} | Kick'
        embed.description = f'{membro} foi expulso por: `{reason}`'
        return await ctx.send(embed=embed)

    @commands.command(usage='{}lock', description='Bloqueia ou desbloqueia os membros de falarem no canal. [Gerenciar Canais]')
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

        await ctx.channel.set_permissions(ctx.guild.default_role, reason=f'Lock | Por: {ctx.author}', send_messages=unlock, read_messages=rms)

        embed = self.bot.embed(ctx)
        embed.title = f'Lock'
        embed.description = f'O canal foi {"des" if unlock == None else ""}bloqueado para o cargo `{ctx.guild.default_role.name}`.'
        await ctx.send(embed=embed)

    @commands.command(usage='{}allow', description='Permite um usuário ver ou desver um canal bloqueado. [Gerenciar Canais]')
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def allow(self, ctx, membro:discord.Member):
        no = ""
        allow = True
        erro = self.bot.erEmbed(ctx)
        try:
            if membro in ctx.channel.members:
                if ctx.channel.overwrites[membro].read_messages == True:
                    no = "não "
                    allow = None
        except KeyError:
            erro.description = "Este membro tem permissão de gerenciar canais, ou o canal não está restrito.\nCaso nada disso se aplique quer dizer que ele tem um cargo com permissão."
            return await ctx.send(embed=erro)

        if no:
            await ctx.channel.set_permissions(membro, reason=f'Allow | Por: {ctx.author}', overwrite=None)
            if membro in ctx.channel.members:
                erro.description = 'Este membro tem permissão de gerenciar canais, ou o canal não está restrito.\nCaso nada disso se aplique quer dizer que ele tem um cargo com permissão.'
                return await ctx.send(embed=erro)

        else:
            await ctx.channel.set_permissions(membro, reason=f'Allow | Por: {ctx.author}', send_messages=allow, read_messages=allow)
        embed = self.bot.embed(ctx)
        embed.title = 'Lock'
        embed.description = f'Agora {membro.mention} {no}pode ver ou mandar mensagens nesse canal.'
        await ctx.send(embed=embed)

    # Nem veja esse comando, ele é muito mal programado / dificil de entender.
    @commands.command(usage='{}embed <json/arquivo>', description='Envia um embed no servidor. [Gerenciar Mensagens]\nGere o json aqui: https://discord.club/embedg/\n\n__OBS__: Qualquer valor inválido será ignorado.')
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, jsn=None):
        # Caso seja maior que 2000 caracteres
        if not jsn:
            if ctx.message.attachments:
                if ctx.message.attachments[0].url.endswith(".txt"):
                    jsn = await self.bot.session.get(ctx.message.attachments[0].url)
                    jsn = await jsn.read()
                    jsn = jsn.decode('utf-8')
            else: # Caso não tenha nada
                raise commands.MissingRequiredArgument(Parameter(name="json", kind=Parameter.POSITIONAL_OR_KEYWORD))

        try:
            jsn = loads(jsn)
        except:
            return await ctx.send('Tem algo de errado com o json, verifique se as virgulas estão corretas ou se não há aspas ou chaves sem fechar.')
        
        msg = jsn.get('content', None)

        invalid = []
        class EmbError(Exception):
            pass

        try:
            jsn_emb = jsn['embed']
        except:
            error = self.bot.erEmbed(ctx, "Erro!")
            error.description = 'Você não informou nenhum embed!'
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
            await ctx.send(f"Falha ao enviar o embed, algo pode estar errado nele!\n\nErro: `{e}`")
        
        if invalid:
            await ctx.send(f'Tudo que foi considerado inválido:\n{"; ".join(invalid)}\n{"`Os valores acima provavelmente foram as causas diretas para o embed não ser enviado.`" if error else ""}\nCheque se algo não está faltando ou não é um valor correto, vá para o <https://embed.discord.website/> e verifique os erros', delete_after=10)

    @commands.has_permissions(manage_messages=True)
    @commands.command(usage='{}vote (emoji-sim) (emoji-nao) [mensagem]', description='Faz uma votação no canal atual. [Gerenciar Mensagens]', aliases=['votacao'])
    async def vote(self, ctx, em1:typing.Optional[discord.Emoji], em2:typing.Optional[discord.Emoji], *, mensagem):
        if not em1:
            em1 = em1s = '✅'
        else:
            em1s = f':{em1.name}:'
        if not em2:
            em2 = em2s = '❌'
        else:
            em2s = f':{em2.name}:'
        try:
            await ctx.message.delete()
        except:
            pass

        mentions = re.findall('<@(!|&)?([0-9]*)>', mensagem)
        mentions = [c for c in mentions if c]

        embed = discord.Embed(title=f'Vote para a pergunta abaixo.', description=mensagem, color=self.bot.color)
        embed.set_footer(text=f'{ctx.author.name} • {str(em1s)} para sim, {str(em2s)} para não.', icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at
        if mentions:
            mentions = [f'<@{c[0]}{c[1]}>' for c in mentions]

        if '@everyone' in mensagem:
            mentions.append('@everyone')

        msg = await ctx.send(embed=embed, content=' '.join(mentions))

        await msg.add_reaction(em1)
        await msg.add_reaction(em2)

def setup(bot):
    bot.add_cog(ServerAdmin(bot))
