import discord
from os import listdir
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
    @commands.command()
    async def reload(self, ctx):
        msg = await ctx.send('Recarregando todas as cogs, aguarde...')
        # Recarregar o cache de traduções
        self.bot._translation_cache = {} 
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

        _msg = f'{sccs} módulos recarregados\n{"Erros:" if errors else ""}\n{"".join(errors)}'
        return await msg.edit(content=_msg)

    @commands.is_owner()
    @commands.command(name='eval')
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
        def fulldir(classe, all = False):
            d = [c for c in dir(classe) if not c.startswith("__")]
            if all:
                d += [c for c in dir(classe) if c.startswith("__")]
            final = {}
            for attr in d:
                final[attr] = getattr(classe, attr)
            return final

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
            'getcmd': getcmd,
            'fdir': fulldir
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
        msgs = []
        for txt in self.bot.paginator(result, 1990):
            msgs.append(await ctx.send(f"```py\n{txt}```"))
        if not msgs:
            return await ctx.send("Nenhuma saida.")
        await msgs[-1].add_reaction('❌')
        try:
            await self.bot.wait_for('reaction_add', timeout=20, check=lambda r, u: u == ctx.author and r.emoji == '❌')
        except Exception as e:
            pass
        await msgs[-1].remove_reaction('❌', ctx.me)
        for k, m in enumerate(msgs):
            if k == len(msgs)-1:
                await m.edit(content='```diff\n- Fechado -```', embed=None)
                break
            await m.delete()

    @commands.is_owner()
    @commands.command()
    async def sudo(self, ctx, member:discord.Member, *, cmd):
        message = ctx.message 
        message.author = member 
        message.content = cmd
        sudo_ctx = await self.bot.get_context(message, cls=ctx.__class__)
        await self.bot.invoke(sudo_ctx)

    @commands.is_owner()
    @commands.command()
    async def botban(self, ctx, member, *, reason):
        with open("assets/json/users_banned.json") as f:
            jsn = json.load(f)
        jsn[member] = reason
        with open("assets/json/users_banned.json", "w") as f:
            f.write(json.dumps(jsn, indent=4))
        embed = self.bot.embed(ctx, invisible=True)
        embed.title = f'{member} foi banido!'
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def botunban(self, ctx, member):
        with open("assets/json/users_banned.json") as f:
            jsn = json.load(f)
        del(jsn[member])
        with open("assets/json/users_banned.json", "w") as f:
            f.write(json.dumps(jsn, indent=4))
        embed = self.bot.embed(ctx, invisible=True)
        embed.title = f'{member} foi desbanido!'
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))