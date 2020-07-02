from discord.ext.commands import Converter 
from discord.ext.commands import PartialEmojiConverter, BadArgument
from discord.ext.commands import EmojiConverter as dEmojiConverter
from emoji import UNICODE_EMOJI

__all__ = ('EmojiConverter',)

class EmojiConverter(Converter):
    # pylint: disable=too-few-public-methods
    """Converte para discord.Emoji, discord.PartialEmoji ou str
    
    1. Tenta converter para Emoji
    2. Tenta converter para PartialEmoji
    3. Verifica se é um emoji unicode.
    """ 

    async def convert(self, ctx, argument):
        try:
            emoji = await dEmojiConverter().convert(ctx, argument)
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
        raise BadArgument(f'{argument} não é um emoji.')