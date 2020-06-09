from discord.ext import commands
from json import load
import itertools
from typing import Optional
from assets.models import menus
import traceback

class SoraContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translation_cache__ = {}
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
        return await self.bot.db.get_prefix(self.guild.id)

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

        if not _file:
            _file = 'commands'

        # Se o arquivo não estiver no cache (normal para primeira execução)
        if not _file in self.__translation_cache__:
            with open(f'translation/{self.lang}/{_file}.json', encoding='utf-8') as jsn:
                self.__translation_cache__[_file] = load(jsn)
        trn = self.__translation_cache__[_file]

        if _file == 'commands' and not _nc:
            try:
                # Já que o arquivo é um comando, ele pega sua tradução
                trn = trn[self.command.qualified_name.replace(' ', '.')]['texts']
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
            return trn.format(**fmt)
        except KeyError:
            return key

class HelpPaginator(menus.baseMenu):
    def __init__(self, page_trn, title, prefix, _index, pages):
        super().__init__(pages, title, '')
        self._prefix = prefix
        self._pagec = page_trn
        if _index != -1:
            self._index = _index
            self.should_add_reactions = lambda: False
        else:
            self._index = _index+1

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
        super().__init__(command_attrs={"aliases": ['ajuda']})
        self._help_index = -1

    async def on_help_command_error(self, ctx, error):
        lines = traceback.format_exception(type(error), error, error.__traceback__, 2)
        trace_txt = ''.join(lines)
        print(trace_txt)

    async def prepare_help_command(self, ctx, command=None):
        self.context.command = self.context.bot.get_command('help')

    async def send_error_message(self, error):
        if error.isnumeric():
            self._help_index = int(error)
            await self.send_bot_help([])
            return
        return await self.context.send(error)

    async def command_not_found(self, string):
        # For Cogs
        with open(f"translation/{await self.context.lang()}/commands.json", encoding='utf-8') as trns:
            trns = load(trns)
            translated = [trns["_cogs"][c].lower() for c in trns["_cogs"]]
            translated.sort()
            if string.lower() in translated or (string.isnumeric() and 0 <= int(string) <= len(translated)):
                if string.isnumeric():
                    return str(string)
                return str(translated.index(string.lower()))

        trn = await self.context.trn()
        return trn['notfound'].format(cmd=string)

    async def subcommand_not_found(self, command, string):
        trn = await self.context.trn()
        if isinstance(command, commands.Group):
            return trn['sub_notfound'][0].format(cmd=command.name, sub=string) 
        return trn['sub_notfound'][1].format(cmd=command.name)

    async def send_bot_help(self, mapping):
        ctx = self.context
        trn = await ctx.trn

        def key(cmd):
            return cmd.cog_name or trn['no_cat']

        cmds = await self.filter_commands(ctx.bot.commands, sort=True, key=key)

        pages = []

        _cogs = []
        _cog_list = ["_bot_cog", "_disco_cog", "_fun_cog", "_mod_cog", "_music_cog", "_utils_cog"]
        for cog, commands in itertools.groupby(cmds, key=key):
            commands = sorted(commands, key = lambda m: m.name)
            if not commands:
                continue

            with open(f"translation/{await ctx.lang()}/commands.json", encoding='utf-8') as trns:
                trns = load(trns)
                
                _cogs.append(cog)
                cog = trns["_cogs"][cog]
                commands = [[trns[c.name]["usage"]] + [trns[c.name]["description"]] for c in commands]

            pages.append((cog, commands))

        if not self._help_index == -1:
            try:
                _pg = _cog_list[self._help_index]
                if not _pg == _cogs[self._help_index]:
                    self._help_index = -1
            except:
                self._help_index = -1
        _index = self._help_index
        self._help_index = -1

        paginator = HelpPaginator(trn['page_c'], trn['emb_title'], self.clean_prefix, _index, pages)
        await paginator.start(ctx)

    async def send_command_help(self, command):
        ctx = self.context
        trn = await ctx.trn
        with open(f'translation/{await ctx.lang()}/commands.json', encoding='utf-8') as _trn:
            _trn = load(_trn)
            cmd_json = _trn[command.qualified_name.replace(' ', '.')]

        embed = await ctx.bot.embed(ctx)
        embed.title = trn['cmd_title'].format(cmd=command.name.title())
        embed.add_field(name=trn['cmd_usage'], value=cmd_json["usage"].format(self.clean_prefix), inline=False)
        embed.add_field(name=trn['cmd_desc'], value=cmd_json["description"], inline=False)
        if command.aliases:
            embed.add_field(name=trn['cmd_aliases'], value=', '.join(command.aliases), inline=False)

        if command.parent:
            embed.add_field(name=trn['cmd_parent'], value=f'{self.clean_prefix}`{command.parent.name}`', inline=False)

        if cmd_json.get("perms"):
            with open(f'translation/{await ctx.lang()}/perms.json') as prms:
                prms = load(prms)
                embed.add_field(name=trn['cmd_perms'], value=', '.join([prms[c].title() for c in cmd_json["perms"]]))
        return await ctx.send(embed=embed)
    
    async def send_group_help(self, group):
        ctx = self.context
        trn = await ctx.trn
        with open(f'translation/{await ctx.lang()}/commands.json', encoding='utf-8') as _trn:
            _trn = load(_trn)
            cmd_json = _trn[group.name]

        embed = await ctx.bot.embed(ctx)
        embed.title = trn['cmd_title'].format(cmd=group.name.title())
        embed.add_field(name=trn['cmd_usage'], value=cmd_json["usage"].format(self.clean_prefix), inline=False)
        embed.add_field(name=trn['cmd_desc'], value=cmd_json["description"], inline=False)
        if group.aliases:
            embed.add_field(name=trn['cmd_aliases'], value=', '.join(group.aliases), inline=False)

        if cmd_json.get("perms"):
            with open(f'translation/{await ctx.lang()}/perms.json') as prms:
                prms = load(prms)
                embed.add_field(name=trn['cmd_perms'], value=', '.join([prms[c].title() for c in cmd_json["perms"]]))

        if group.commands:
            sub = ''
            for cmd in group.commands:
                _sub_jsn = _trn[cmd.qualified_name.replace(' ', '.')]
                sub += f'{_sub_jsn["usage"].format(self.clean_prefix)} — {_sub_jsn["description"]}\n\n'
            embed.add_field(name=trn['group_sub'], value=sub)

        return await ctx.send(embed=embed)
