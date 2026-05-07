from discord.ext import commands

from ..bot import TehBot


class UserCog(commands.Cog):
    def __init__(self, bot: TehBot):
        self.bot = bot


async def setup(bot: TehBot):
    await bot.add_cog(UserCog(bot))
