from discord import Member, Message
from discord.ext import commands

from .resolver import buildContext
from .types import I18nContext, Personality


async def toI18nContext(
    ctx: commands.Context | Message, db_settings: dict, streak: int | None = 1
) -> I18nContext:
    from src.config_loader import global_config
    guild_id_str = str(ctx.guild.id) if ctx.guild else None

    bot_nick = ctx.guild.me.display_name if ctx.guild else None

    interaction_locale = (
        str(ctx.interaction.locale)
        if isinstance(ctx, commands.Context)
        and hasattr(ctx, "interaction") and ctx.interaction
        else None
    )
    locale_str = (
        db_settings.get("language")
        or interaction_locale
        or global_config.get("default_language", "en_US")
    )

    is_admin = False
    if isinstance(ctx.author, Member):
        is_admin = ctx.author.guild_permissions.administrator

    personality = Personality(
        type=db_settings.get(
            "personality_type", global_config.get("default_personality", "casual")
        ),
        intensity=db_settings.get("intensity", "normal"),
    )

    return buildContext(
        {
            "user_id": str(ctx.author.id),
            "bot_nick": bot_nick,
            "guild_id": guild_id_str,
            "locale": locale_str,
            "is_admin": is_admin,
            "personality": personality,
            "emotion": db_settings.get("current_emotion", "happy"),
            "streak": streak or 0,
        }
    )
