import discord
import pyfiglet
import validators
from discord.ext import commands
from aiohttp import BasicAuth 
from os import getenv
from datetime import datetime

class Utils(commands.Cog, name='Utilitários'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ascii', usage='{}ascii [fonte] [texto]',
    description='Envia um texto ascii provido pelo figlet\nFontes encontradas em: http://www.figlet.org/examples.html')
    async def _ascii(self, ctx, fonte, *, texto):
        embed = self.bot.embed(ctx, invisible=True)
        embed.description = 'Aguarde, carregando...'
        msg = await ctx.send(embed=embed)
        try:
            fnt = pyfiglet.Figlet(font=fonte)
        except pyfiglet.FontNotFound:
            embed = self.bot.erEmbed(ctx, 'Fonte inválida.')
            embed.description = f'A fonte que você inseriu não existe.\nFontes encontradas em: http://www.figlet.org/examples.html'
            return await msg.edit(embed=embed)

        txt = fnt.renderText(texto)
        if len(txt) > 2000-10:
            embed = self.bot.erEmbed(ctx, 'Texto inválido.')
            embed.description = 'O texto que você inseriu é muito grande para ser convertido para ascii.'
            return await msg.edit(embed=embed)

        await msg.edit(embed=None, content=f'```css\n{txt.rstrip()}```')       

    @commands.group(
        usage='{}qrcode [texto] (#cor:hex)',
        description='Gera um código QR\nSe o texto começar com `read`, coloque tudo entre aspas.', 
        aliases=['qr'], 
        invoke_without_command=True, case_insensitive=True)
    async def qrcode(self, ctx, *, texto):
        if ctx.invoked_subcommand is None:
            try:
                texto, cor = texto.split('#')
            except:
                cor = 'cccccc'

            embed = self.bot.embed(ctx, invisible=True)
            embed.description = 'Carregando, aguarde...'

            m = await ctx.send(embed=embed)
            
            qrcode = await self.bot.session.get(f'http://api.qrserver.com/v1/create-qr-code/?data={texto}&size=500x500&color={cor}&bgcolor=2F3136')
            
            embed = self.bot.embed(ctx)
            embed.title = 'QR Code'
            embed.set_image(url=qrcode.url)

            await m.edit(embed=embed)

    @qrcode.command(usage='{}qrcode read <imagem/url>', description='Lê um código QR.')
    async def read(self, ctx, *, url=None):
        nofile = self.bot.erEmbed(ctx, 'Nenhum arquivo.')
        nofile.description = 'Você não informou nenhuma imagem.'
        if not url:
            try:
                url = ctx.message.attachments[0].url
            except:
                return await ctx.send(embed=nofile)

        response = await self.bot.session.get(f'http://api.qrserver.com/v1/read-qr-code/?fileurl={url}')

        embed = self.bot.embed(ctx, invisible=True)
        embed.description = 'Carregando...'
        m = await ctx.send(embed=embed)
        try:
            async with response:
                response = await response.json()
                response = response[0]

        except:
            return await m.edit(embed=nofile)
        if response["symbol"][0]["error"]:
            embed = self.bot.erEmbed(ctx, 'Imagem inválida!')
            embed.description = 'Esta imagem não pode ser baixada ou lida.'
            return await m.edit(embed=embed)

        embed = self.bot.embed(ctx)
        embed.title = 'QR Code | Read'
        embed.add_field(name='Saída:', value=response["symbol"][0]["data"], inline=False)
        embed.add_field(name='Tipo:', value=response["type"])
        await m.edit(embed=embed)

    @commands.command(usage='{}barcode [texto]', description='Gera um código de barras.')
    async def barcode(self, ctx, *, texto):
        barcode = await self.bot.session.get(f'http://bwipjs-api.metafloor.com/?bcid=code128&text={texto}')

        try:
            text = await barcode.text()
        except:
            text = 'Isso é uma imagem.' # Gambiarra kkk
        if text.startswith("Error:"):
            embed = self.bot.erEmbed(ctx)
            embed.description = 'Algum erro ocorreu ao gerar a imagem, verifique o texto que você usou.'
            return await ctx.send(embed=embed)
        
        embed = self.bot.embed(ctx)
        embed.title = 'Código de Barras'
        embed.set_image(url=barcode.url)
        await ctx.send(embed=embed)

    @commands.command(usage='{}mcbody [nick]', description='Exibe a skin de um jogador do minecraft. (original)')
    async def mcbody(self, ctx, nick):
        nick = nick[:200]

        embed = self.bot.embed(ctx)
        embed.description = f'[Baixar Skin](https://minecraft.tools/download-skin/{nick}) | [Modelo 3d](https://mc-heads.net/body/{nick})'
        embed.set_author(name=f'Skin de {nick}', icon_url=f'https://minotar.net/helm/{nick}/300.png')
        embed.set_image(url=f'https://mc-heads.net/body/{nick}')
        embed.set_thumbnail(url=f'https://minecraftskinstealer.com/api/v1/skin/render/fullbody/{nick}/700')
        await ctx.send(embed=embed)

    @commands.command(usage='{}github [usuario]', description='Exibe informações sobre um usuário/repositório do github.')
    async def github(self, ctx, usuario):
        base_url = f'https://api.github.com/users/{usuario}'
        git_name, git_token = getenv("git_token").split(":")
        auth = BasicAuth(git_name, git_token, 'utf-8')
        user = await self.bot.session.get(base_url, auth=auth)

        if user.status != 200:
            erro = self.bot.erEmbed(ctx, 'Erro!')
            if user.status == 401:
                erro.description = 'O token do github está errado!\nContate um desenvolvedor.'
           
            if user.status == 403:
                erro.description = 'O bot está em ratelimit do github, contate um desenvolvedor e aguarde.'

            if user.status == 404:
                erro = self.bot.erEmbed(ctx, 'Não encontrado.')
                erro.description = 'O usuário que você informou, não foi encontrado.\n Verifique se o nome informado corresponde ao usado no link.'
    
            return await ctx.send(embed=erro)
        
        user = await user.json()

        embed = self.bot.embed(ctx)
        embed.description = user.get("bio", discord.Embed.Empty)

        nome = user["name"] if user["name"] else user["login"]
        embed.set_author(name=f'Github de {nome}', icon_url=user["avatar_url"], url=user["html_url"])

        embed.add_field(name=f'Nome de usuário:', value=user["login"], inline=False)
        embed.add_field(name=f'Carregando repositórios:', value='Carregando...', inline=False)
        embed.add_field(name=f'Seguidores:', value=f'Este usuário é seguido por {user["followers"]} pessoas\nEnquanto segue {user["following"]} pessoas.', inline=False)

        if user["email"]:
            embed.add_field(name=f'Email:', value=user["email"])

        created = datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        created_tz = self.bot.utc_to_timezone(created, self.bot.timezone)
        embed.add_field(name='Conta criada em:', value=f'{created_tz.strftime("%d/%m/%Y as %H:%M")} ({"".join(self.bot.getTime(created)[0].replace(", ", "").replace("e ", ""))} atrás)')

        m = await ctx.send(embed=embed)

        embed.remove_field(1)
        repos = await self.bot.session.get(base_url + '/repos', auth=auth)
        repos = await repos.json()

        user_repos = [f'[{c["name"]}]({c["html_url"]}) ==={c["fork"]}'.replace("===True", "_forked_").replace('===False', '') for c in repos]
        if len(user_repos) > 15:
            user_repos = user_repos[:15]
            user_repos.append(f'E mais {user["public_repos"]-15} repositórios')

        user_repos = ["Nenhum."] if not user_repos else user_repos
        embed.insert_field_at(1, name=f'Este usuário tem {user["public_repos"]} repositórios:', value='\n'.join(user_repos), inline=False)
        await m.edit(embed=embed)

    @commands.command(usage='{}guild [id]', description='Exibe informações sobre uma guild (discord widget).')
    async def guild(self, ctx):
        raise NotImplementedError

    @commands.command(usage='{}addbot [bot (no server)] (permissões)', description='Pega o convite de um bot.')
    async def addbot(self, ctx, bot:discord.Member, permissions='8'):
        if not bot.bot: # Estranho esse bot.bot kkkkk
            embed = self.bot.erEmbed(ctx, 'Membro inválido!')
            embed.description = 'Este membro não é um bot!'
            return await ctx.send(embed=embed)
        invalid = False
        if not permissions.isdigit():
            invalid = True
            permissions = '8'
        base_url = 'https://discordapp.com/oauth2/authorize?scope=bot&client_id={}&permissions={}'        
        embed = self.bot.embed(ctx)
        embed.title = f'Aqui está o convite do bot {bot.name}'
        embed.description = f'{base_url.format(bot.id, permissions)}\n\n{"A permissão que você digitou estava inválida, 8 no lugar." if invalid else ""}'
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utils(bot))