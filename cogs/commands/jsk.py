from discord.utils import find
from jishaku.cog import JishakuBase, jsk
from jishaku.metacog import GroupCogMeta
from discord.ext.commands import NotOwner

class Jishaku(JishakuBase, metaclass=GroupCogMeta, command_parent=jsk):
    async def cog_check(self, ctx):
        m = self.bot.get_guild(675889958262931488).get_member(ctx.author.id)
        if m:
            if find(lambda r: r.id == 676516943632531516, m.roles): 
                return True
        raise NotOwner()

def setup(bot): 
    bot.add_cog(Jishaku(bot=bot))