import discord
from os import listdir
import io
import typing
import ast
import json
import inspect
from discord.ext import commands

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

class Owner(commands.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(usage='Sigiloso.', description='Sigiloso.')
    async def reload(self, ctx):
        msg = await ctx.send('Recarregando todas as cogs, aguarde...')
        error = []
        sccs = 0

        for fldr in listdir('cogs'):
            for file in listdir(f'cogs/{fldr}'):
                if file.startswith('_') or not file.endswith('.py'):
                    continue

                file = file.replace(".py", "")

                try:
                    self.bot.reload_extension(f'cogs.{fldr}.{file}')
                except commands.ExtensionNotLoaded:
                    try:
                        self.bot.load_extension(f'cogs.{fldr}.{file}')
                    except Exception as e:
                        error.append((f'{fldr}/{file}', type(e).__name__, e))
                    else:
                        sccs += 1

                except Exception as e:
                    error.append((f'{fldr}/{file}', type(e).__name__, e))
                else:
                    sccs += 1

        errors = [f'**{c[0]}:** {c[1]}: ```{c[2]}```\n' for c in error]

        embed = self.bot.embed(ctx)
        embed.title = 'Reload'
        embed.description = f'{sccs} módulos recarregados\n{"Erros:" if errors else ""}\n{"".join(errors)}'
        return await msg.edit(embed=embed, content='')

    @commands.is_owner()
    @commands.command(name='eval', usage='Sigiloso.', description='Sigiloso.')
    async def _eval(self, ctx, *, cmd):
        # Funções
        def getsource(arquivo):
            with open(arquivo, encoding='utf-8') as fl:
                return fl.read()
        def getcmd(cmd):
            cmd = self.bot.get_command(cmd)
            if not cmd:
                raise NameError("Comando não encontrado.")
            return inspect.getsource(cmd.callback)
        
        func = "_eval_expr"
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {func}():\n{cmd}"

        env = {
            'self': self,
            'discord': discord,
            'source': getsource,
            'commands': commands,
            'ctx': ctx,
            'imp': __import__,
            'getcmd': getcmd
        }

        try:
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = await eval(f"{func}()", env)
            if inspect.isawaitable(result):
                result = await result

        except Exception as e:
            result=f'Erro:\n\n{type(e).__name__}: {e}'
            try:
                await ctx.message.add_reaction('❎')
            except:
                pass
        else:
            try:
                await ctx.message.add_reaction('✅')
            except:
                pass
        for txt in self.bot.paginator(result, 1990):
            await ctx.send(f"```py\n{txt}```")

    @commands.is_owner()
    @commands.command(usage='Sigiloso.', description='Sigiloso.')
    async def sudo(self, ctx, member:discord.Member, *, cmd):
        message = ctx.message 
        message.author = member 
        message.content = cmd
        await self.bot.process_commands(message)

    @commands.is_owner()
    @commands.command(usage='Sigiloso.', description='Sigiloso.')
    async def botban(self, ctx, member, *, reason):
        with open("assets/users_banned.json") as f:
            jsn = json.load(f)
        jsn[member] = reason
        with open("assets/users_banned.json", "w") as f:
            f.write(json.dumps(jsn, indent=4))
        embed = self.bot.embed(ctx, invisible=True)
        embed.title = f'{member} foi banido!'
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(usage='Sigiloso.', description='Sigiloso.')
    async def botunban(self, ctx, member):
        with open("assets/users_banned.json") as f:
            jsn = json.load(f)
        del(jsn[member])
        with open("assets/users_banned.json", "w") as f:
            f.write(json.dumps(jsn, indent=4))
        embed = self.bot.embed(ctx, invisible=True)
        embed.title = f'{member} foi desbanido!'
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Owner(bot))