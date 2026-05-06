from datetime import datetime

from pytz import UTC

from .types import I18nContext, Personality, PersonalityToneType


def buildContext(input_data: dict) -> I18nContext:
    hour = datetime.now(UTC).hour
    user_id = input_data.get("user_id") or input_data.get("userId")
    locale = str(input_data.get("locale", "en"))

    if not user_id:
        raise ValueError("user_id is required to build I18nContext")

    return I18nContext(
        user_id=str(user_id),
        guild_id=input_data.get("guild_id"),
        is_guild=bool(input_data.get("guild_id")),
        is_dm=not bool(input_data.get("guild_id")),
        locale=locale,
        hour=hour,
        is_admin=input_data.get("is_admin", False),
        is_new_user=input_data.get("is_new_user", False),
        level=input_data.get("level"),
        personality=input_data.get(
            "personality",
            Personality(type=PersonalityToneType.CASUAL, intensity="normal"),
        ),
        emotion=input_data.get("emotion", "happy"),
        streak=input_data.get("streak", 1),
    )
