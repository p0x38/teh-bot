from datetime import datetime

from pytz import UTC

from .types import EmotionType, I18nContext, Personality, PersonalityToneType


def build_i18n_context(
    user_id: str,
    locale: str,
    guild_id: str | None = None,
    is_admin: bool = False,
    is_new_user: bool = False,
    level: int | None = None,
    personality: Personality | None = None,
    emotion: EmotionType = EmotionType.HAPPY,
    streak: int = 1,
) -> I18nContext:
    return I18nContext(
        user_id=user_id,
        guild_id=guild_id,
        is_guild=bool(guild_id),
        is_dm=not bool(guild_id),
        locale=locale,
        hour=datetime.now(UTC).hour,
        is_admin=is_admin,
        is_new_user=is_new_user,
        level=level,
        personality=personality
        or Personality(type=PersonalityToneType.CASUAL, intensity="normal"),
        emotion=emotion,
        streak=streak,
    )
