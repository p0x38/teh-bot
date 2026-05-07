from discord.ext import commands

from ..bot import TehBot
from ..contexts.context import TehContext


class UsageTracker(commands.Cog):
    def __init__(self, bot: TehBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: TehContext):
        await self.bot.db.track_command_usage(
            guild_id=ctx.guild.id if ctx.guild else 0,
            user_id=ctx.author.id,
            command=ctx.command.qualified_name if ctx.command else 'Unknown'
        )


async def setup(bot):
    await bot.add_cog(UsageTracker(bot))
