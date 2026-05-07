from discord.ext import commands

from src.bot import TehBot
from src.i18n import toI18nContext

from ..contexts.context import TehContext


class SettingsCog(commands.Cog):
    def __init__(self, bot: TehBot):
        self.bot = bot

    @commands.group(name="settings", invoke_without_command=True)
    async def settings_group(self, ctx: TehContext):
        usage = (
            f"**Settings Categories**\n"
            f"`{ctx.prefix}settings guild` - Server-wide configuration\n"
            f"`{ctx.prefix}settings user` - Your personal preferences\n"
            f"`{ctx.prefix}settings bot` - Global bot info (Admin only)"
        )

        await ctx.send(usage)

    # --- GUILD PREFERENCES ---#
    @settings_group.group(name="guild", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def guild_settings(self, ctx: TehContext):
        await ctx.send(f"Usage: `{ctx.prefix}settings guild <language|personality>")

    @guild_settings.command(name="language")
    async def guild_language(self, ctx: TehContext, lang: str):
        if not ctx.guild:
            locale_str = str(ctx.interaction.locale) if ctx.interaction else "en"
            return await ctx.reply(
                self.bot.translator.t(locale_str, "errors-settings-guild-only")
            )

        await self.bot.db.update_guild_settings(ctx.guild.id, {"locale": lang})

        await self.bot.cache.delete(f"config:guild:{ctx.guild.id}")
        await ctx.send(
            self.bot.translator.t(
                lang, "commands-settings-language-updateds", new_lang=lang
            )
        )

    @guild_settings.command(name="personality")
    async def set_personality(self, ctx: TehContext, style: str):
        if not ctx.guild:
            locale_str = str(ctx.interaction.locale) if ctx.interaction else "en"
            return await ctx.reply(
                self.bot.translator.t(locale_str, "errors-settings-guild-only")
            )

        new_data = await self.bot.db.update_guild_settings(
            ctx.guild.id, {"personality_type": style}
        )

        await self.bot.cache.delete(f"config:guild:{ctx.guild.id}")

        i18n_ctx = await toI18nContext(ctx, new_data)

        response = self.bot.translator.t(
            i18n_ctx.locale, "settings-updated", ctx=i18n_ctx, style=style
        )
        await ctx.send(response)

    # --- USER PREFERENCES --- #
    @settings_group.group(name="user", invoke_without_command=True)
    async def user_settings(self, ctx: TehContext):
        await ctx.send(f"Usage: `{ctx.prefix}settings user <timezone|privacy>")

    @user_settings.command(name="timezone")
    async def user_tz(self, ctx: TehContext, tz: str):
        await self.bot.cache.delete(f"config:user:{ctx.author.id}")
        await ctx.send(f"Your timezone is now `{tz}`.")

    # --- BOT PREFERENCES --- #
    @settings_group.group(name="bot", invoke_without_command=True)
    @commands.is_owner()
    async def global_settings(self, ctx: TehContext):
        await ctx.send(f"Usage: `{ctx.prefix}settings bot <maintenance>")


async def setup(bot):
    await bot.add_cog(SettingsCog(bot))
