"""Conversores de comandos"""

from discord import NotFound
from discord.ext.commands import Converter 
from discord.ext.commands import PartialEmojiConverter, MemberConverter, BadArgument
from discord.ext.commands import EmojiConverter as EmConvert
from emoji import UNICODE_EMOJI

__all__ = ('EmojiConverter', 'UserConverter')

class EmojiConverter(Converter):
    # pylint: disable=too-few-public-methods
    """Converte para discord.Emoji, discord.PartialEmoji ou str
    
    1. Tenta converter para Emoji
    2. Tenta converter para PartialEmoji
    3. Verifica se é um emoji unicode.
    """ 

    async def convert(self, ctx, argument):
        try:
            emoji = await EmConvert().convert(ctx, argument)
        except BadArgument:
            pass
        else:
            return emoji
        
        try:
            emoji = await PartialEmojiConverter().convert(ctx, argument)
        except BadArgument:
            pass
        else:
            return emoji 

        if argument in UNICODE_EMOJI:
            return argument
        raise BadArgument(f'Emoji "{argument}" not found.')

class UserConverter(Converter):
    #pylint: disable=too-few-public-methods
    """Converte para discord.Member ou discord.User

    1. Tenta converter para membro.
    2. Tenta dar fetch_user (se for um número)
    """

    async def convert(self, ctx, argument):
        try:
            member = await MemberConverter().convert(ctx, argument)
        except BadArgument:
            pass
        else:
            return member
        
        if argument.isnumeric():
            user = ctx.bot.get_user(int(argument))
            if not user:
                try:
                    user = await ctx.bot.fetch_user(int(argument))
                except:
                    pass
                else:
                    return user 
        
        raise BadArgument(f'User "{argument}" not found.')
