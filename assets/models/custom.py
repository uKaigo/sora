from discord.ext import commands
from json import load
import itertools
from typing import Optional
from assets.models import menus
import traceback

class SoraContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lang = ''

    @property
    def lang(self) -> str:
        """Retorna a linguagem do servidor"""
        if not hasattr(self, '_lang') or not self._lang:
            raise RuntimeError('Linguagem não definida.')
        return self._lang

    # A ser descontinuado
    @property
    async def trn(self) -> Optional[dict]:
        _trn_jsn = await self.bot.get_translation(self)
        try:
            return _trn_jsn['texts']
        except TypeError:
            return None

    async def guild_prefix(self) -> Optional[str]:
        """Retorna a prefixo do servidor"""
        return await self.bot.db.guild_get(self.guild.id, 'prefix')

    # Substituir o ctx.trn
    def t(self, key, **fmt) -> str:
        """Retorna uma tradução.
        
        Configurações:
            _e: Erro
            _f: Arquivo
            _nc: Nao é um comando

        Keywords:  
            Passado para um .format
        """

        key = str(key)

        # Pega configurações
        _error = fmt.pop('_e', None)
        _file = fmt.pop('_f', None)
        _nc = fmt.pop('_nc', False)

        if _error and not _file: _file='errors'

        if not _file: _file = 'commands'

        # Se o arquivo não estiver no cache do bot, ele salvará
        if not _file in self.bot._translation_cache.get(self.lang, {}):    
            # Salvar a linguagem antes de salvar o arquivo
            if not self.lang in self.bot._translation_cache: 
                self.bot._translation_cache[self.lang] = dict()
            
            with open(f'translation/{self.lang}/{_file}.json', encoding='utf-8') as jsn:
                self.bot._translation_cache[self.lang][_file] = load(jsn)
        
        trn = self.bot._translation_cache[self.lang][_file]
        if _file == 'commands' and not _nc:
            try:
                # Já que o arquivo é um comando, ele pega sua tradução
                trn = trn[self.command.qualified_name]['texts']
            except KeyError:
                return key

        if _error:
            try:
                trn = trn[_error]
            except KeyError:
                return key

        try:
            for k in key.split('.'):
                trn = trn[int(k) if k.isnumeric() else k]
            if fmt:
                return trn.format(**fmt)
            return trn
        except KeyError:
            return key

class HelpPaginator(menus.baseMenu):
    def __init__(self, page_trn, title, prefix, pages):
        super().__init__(pages, title, '')
        self._prefix = prefix
        self._pagec = page_trn

    @property
    async def embed(self):
        current = self.pages[self._index]

        cog = current[0]
        commands = current[1]

        embed = await self.bot.embed(self.ctx)
        
        if self.should_add_reactions():
            embed.set_author(name=self._pagec.format(page=self._index+1, max=len(self.pages)))
        
        embed.title = self._title.format(cog=cog)
        
        for cmd, description in commands:
            embed.add_field(name=cmd.format(self._prefix), value=description, inline=False)
        
        return embed

class SoraHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={'aliases': ['ajuda']})
        self._help_index = -1

    async def on_help_command_error(self, ctx, error):
        lines = traceback.format_exception(type(error), error, error.__traceback__, 2)
        trace_txt = ''.join(lines)
        print(trace_txt)

    async def prepare_help_command(self, ctx, command=None):
        # Necessário para o sistema de tradução funcionar
        self.context.command = self.context.bot.get_command('help')

    async def send_error_message(self, error):
        return await self.context.send(error)

    async def command_not_found(self, string):
        return self.context.t('notfound', cmd=string)

    async def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group):
            return self.context.t('sub_notfound.0', cmd=command.name, sub=string) 
        return self.context.t('sub_notfound.1', cmd=command.name)

    async def send_bot_help(self, mapping):
        ctx = self.context

        def key(cmd):
            return cmd.cog_name or ctx.t('no_cat')

        cmds = await self.filter_commands(ctx.bot.commands, sort=True, key=key)

        pages = []

        _cogs = []
        _cog_list = [cog[0] for cog in ctx.t('_cogs', _nc=1).items()]

        for cog, _commands in itertools.groupby(cmds, key=key):
            _commands = sorted(_commands, key = lambda m: m.name)
            if not _commands:
                continue
            
            cog = ctx.t(f'_cogs.{cog}', _nc=1)
            _cmds = []
            for cmd in _commands:
                _cmd_name = cmd.qualified_name
                _cmds.append([ctx.t(f'{_cmd_name}.usage', _nc=1), ctx.t(f'{_cmd_name}.description', _nc=1)])

            pages.append((cog, _cmds))

        paginator = HelpPaginator(ctx.t('page_c'), ctx.t('emb_title'), self.clean_prefix, pages)
        await paginator.start(ctx)

    async def send_command_help(self, command):
        ctx = self.context
        cmd_name = command.qualified_name

        embed = await ctx.bot.embed(ctx)
        embed.title = ctx.t('cmd_title', cmd=command.name.title())
        embed.add_field(name=ctx.t('cmd_usage'), value=ctx.t(f'{cmd_name}.usage', _nc=1).format(self.clean_prefix), inline=False)
        embed.add_field(name=ctx.t('cmd_desc'), value=ctx.t(f'{cmd_name}.description', _nc=1), inline=False)
        if command.aliases:
            embed.add_field(name=ctx.t('cmd_aliases'), value=', '.join(command.aliases), inline=False)

        if command.parent:
            embed.add_field(name=ctx.t('cmd_parent'), value=f'{self.clean_prefix}`{command.parent.name}`', inline=False)

        if ctx.t(f'{cmd_name}.perms', _nc=1) != f'{cmd_name}.perms':
            embed.add_field(name=ctx.t('cmd_perms'), value=', '.join([ctx.t(c, _f='perms').title() for c in ctx.t(f'{cmd_name}.perms', _nc=1)]))
        return await ctx.send(embed=embed)
    
    async def send_group_help(self, group):
        ctx = self.context
        cmd_name = group.name 

        embed = await ctx.bot.embed(ctx)
        embed.title = ctx.t('cmd_title', cmd=group.name.title())
        embed.add_field(name=ctx.t('cmd_usage'), value=ctx.t(f'{cmd_name}.usage', _nc=1).format(self.clean_prefix), inline=False)
        embed.add_field(name=ctx.t('cmd_desc'), value=ctx.t(f'{cmd_name}.description', _nc=1), inline=False)
        if group.aliases:
            embed.add_field(name=ctx.t('cmd_aliases'), value=', '.join(group.aliases), inline=False)

        if ctx.t(f'{cmd_name}.perms', _nc=1) != f'{cmd_name}.perms':
            embed.add_field(name=ctx.t('cmd_perms'), value=', '.join([ctx.t(c, _f='perms').title() for c in ctx.t(f'{cmd_name}.perms', _nc=1) ]))
        
        if group.commands:
            sub = ''
            for cmd in group.commands:
                _sub_name = cmd.qualified_name
                sub += f'{ctx.t(f"{_sub_name}.usage", _nc=1).format(self.clean_prefix)} — {ctx.t(f"{_sub_name}.description", _nc=1)}\n\n'
            embed.add_field(name=ctx.t('group_sub'), value=sub)

        return await ctx.send(embed=embed)
