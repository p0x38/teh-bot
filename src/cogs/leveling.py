from discord import Message
from discord.ext import commands

from src.bot import TehBot
from src.databases.models import UserXP
from src.i18n import toI18nContext
from src.leveling.tiers import get_tier


class LevelingCog(commands.Cog):
    def __init__(self, bot: TehBot):
        self.bot = bot
        self.xp_cooldown = 10
        self.cooldowns = {}

    def calculate_xp_to_add(self, message: str):
        content = message.strip()
        if not content:
            return 0

        return min(len(content.split(" ")) + len(content), 10000)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot or not message.guild:
            return

        xp_gain = await self.bot.xp.try_gain_xp(message)
        if not xp_gain:
            return

        previous_xp = await self.bot.db.get_user_level(message.author.id, message.guild.id)

        user, leveled_up = await self.bot.db.add_xp(
            message.guild.id,
            message.author.id,
            xp_gain
        )

        if leveled_up:
            await self._send_level_up(message, user.level, previous_xp)

    async def _send_level_up(self, message: Message, level: int, previous: UserXP):
        if not message.guild:
            return

        ctx = await self.bot.db.get_guild_settings(message.guild.id)
        i18n_ctx = await toI18nContext(message, ctx.data)

        tier = get_tier(level)

        is_same_tier = get_tier(previous.level) == tier

        text = self.bot.translator.t(
            i18n_ctx.locale,
            "messages:level-up",
            ctx=i18n_ctx,
            level=level,
            is_same_tier=is_same_tier,
            user=message.author.mention,
            tier=tier
        )

        await message.channel.send(text)

    @commands.command(name="rank")
    @commands.guild_only()
    async def rank(self, ctx: commands.Context):
        data = await self.bot.db.get_user_level(ctx.author.id, ctx.guild.id)  # type: ignore

        await ctx.send(
            f"Level: {data.level} | XP: {data.xp}"
        )

    @commands.command(name="leaderboard")
    @commands.guild_only()
    async def leaderboard(self, ctx: commands.Context):
        top = await self.bot.db.get_leveling_leaderboard(ctx.guild.id)  # type: ignore

        lines = []
        for i, user in enumerate(top, start=1):
            member = ctx.guild.get_member(user.user_id)  # type: ignore
            name = member.name if member else f"User {user.user_id}"

            lines.append(
                f"{i}. {name} — Lv.{user.level} ({user.xp} XP)"
            )

        await ctx.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(LevelingCog(bot))
