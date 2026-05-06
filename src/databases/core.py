import os
from datetime import datetime, timedelta

from pydantic import ValidationError
from pytz import UTC
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import attributes

from src.config.schema import DatabaseConfig
from src.leveling.tiers import xp_for_level

from ..i18n.types import UserEmotionState
from .models import Base, CommandUsage, GuildConfig, UserProfile, UserXP


def load_db_config() -> DatabaseConfig:
    try:
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT") or 5432),
            user=str(os.getenv("DB_USER")),
            password=str(os.getenv("DB_PASSWORD")),
            name=str(os.getenv("DB_NAME")),
            driver=os.getenv("DB_DRIVER", "asyncpg"),
        )
    except ValidationError as e:
        raise RuntimeError(f"Invalid DB config: {e}") from e


class Database:
    def __init__(self):
        config = load_db_config()
        database_url = config.build_url()

        self.engine = create_async_engine(database_url, echo=False)
        self.session_maker = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_guild_settings(self, guild_id: int) -> GuildConfig:
        async with self.session_maker() as session:
            stmt = select(GuildConfig).where(GuildConfig.guild_id == guild_id)
            result = await session.execute(stmt)
            config = result.scalar_one_or_none()

            if not config:
                config = GuildConfig(guild_id=guild_id, data={})
                session.add(config)
                await session.commit()

            return config

    async def update_guild_settings(self, guild_id: int, new_settings: dict):
        async with self.session_maker() as session:
            stmt = select(GuildConfig).where(GuildConfig.guild_id == guild_id)
            result = await session.execute(stmt)
            config = result.scalar_one_or_none()

            if not config:
                config = GuildConfig(guild_id=guild_id, data={})
                session.add(config)

            current_data = dict(config.data)
            current_data.update(new_settings)

            config.data = current_data
            attributes.flag_modified(config, "data")

            await session.commit()
            return current_data

    async def add_xp(self, guild_id: int, user_id: int, amount: int):
        async with self.session_maker() as session:
            stmt = select(UserXP).where(
                UserXP.guild_id == guild_id,
                UserXP.user_id == user_id
            )
            result = await session.execute(stmt)

            user = result.scalar_one_or_none()
            if not user:
                user = UserXP(guild_id=guild_id, user_id=user_id, xp=0, level=0)
                session.add(user)

            user.xp += amount

            leveled_up = False
            while user.xp >= xp_for_level(user.level):
                user.xp -= xp_for_level(user.level)
                user.level += 1
                leveled_up = True

            await session.commit()
            return user, leveled_up

    async def get_user_level(self, user_id: int, guild_id: int) -> UserXP:
        async with self.session_maker() as session:
            stmt = select(UserXP).where(
                UserXP.user_id == user_id,
                UserXP.guild_id == guild_id,
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                user = UserXP(user_id=user_id, guild_id=guild_id, xp=0, level=0)
                session.add(user)
                await session.commit()

            return user

    async def get_leveling_leaderboard(self, guild_id: int, limit: int = 10):
        async with self.session_maker() as session:
            stmt = (
                select(UserXP)
                .where(UserXP.guild_id == guild_id)
                .order_by(UserXP.level.desc(), UserXP.xp.desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            return result.scalars().all()

    async def track_command_usage(self, guild_id: int, user_id: int, command: str):
        async with self.session_maker() as session:
            session.add(
                CommandUsage(
                    guild_id=guild_id,
                    user_id=user_id,
                    command=command
                )
            )
            await session.commit()

    async def get_trending_commands(self, guild_id: int, limit: int = 5):
        async with self.session_maker() as session:
            since = datetime.now(UTC) - timedelta(hours=24)

            stmt = (
                select(
                    CommandUsage.command,
                    func.count(CommandUsage.id).label("count")
                )
                .where(
                    CommandUsage.guild_id == guild_id,
                    CommandUsage.timestamp >= since
                )
                .group_by(CommandUsage.command)
                .order_by(func.count(CommandUsage.id).desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            return result.all()

    async def get_user_profile(self, user_id: int) -> UserProfile:
        async with self.session_maker() as session:
            stmt = select(UserProfile).where(UserProfile.user_id == user_id)
            result = await session.execute(stmt)

            profile = result.scalar_one_or_none()

            if not profile:
                profile = UserProfile(user_id=user_id, data={})
                session.add(profile)
                await session.commit()

            return profile

    async def get_user_locale(self, user_id: int) -> str | None:
        profile = await self.get_user_profile(user_id)
        return profile.locale

    async def set_user_locale(self, user_id: int, locale: str):
        async with self.session_maker() as session:
            profile = await session.get(UserProfile, user_id)

            if not profile:
                profile = UserProfile(user_id=user_id, data={})
                session.add(profile)

            profile.locale = locale
            await session.commit()

    async def get_user_personality(self, user_id: int) -> dict | None:
        profile = await self.get_user_profile(user_id)
        return profile.data.get("personality")

    async def set_user_personality(self, user_id: int, personality: dict):
        async with self.session_maker() as session:
            profile = await session.get(UserProfile, user_id)

            if not profile:
                profile = UserProfile(user_id=user_id, data={})
                session.add(profile)

            data = dict(profile.data)
            data["personality"] = personality

            profile.data = data
            attributes.flag_modified(profile, "data")

            await session.commit()

    async def get_emotion_state(self, user_id: int) -> UserEmotionState:
        profile = await self.get_user_profile(user_id)

        raw = profile.data.get("emotion_state")

        if not raw:
            state = UserEmotionState()
        else:
            raw_last_seen = raw.get("last_seen")

            if raw_last_seen:
                last_seen = datetime.fromisoformat(raw_last_seen)
            else:
                last_seen = datetime.now(UTC)

            state = UserEmotionState(
                friendliness=raw.get("friendliness", 0.0),
                annoyance=raw.get("annoyance", 0.0),
                last_seen=last_seen
            )

        return state

    async def save_emotion_state(self, user_id: int, state: UserEmotionState):
        async with self.session_maker() as session:
            stmt = select(UserProfile).where(UserProfile.user_id == user_id)
            result = await session.execute(stmt)
            profile = result.scalar_one()

            data = dict(profile.data)
            data["emotion_state"] = {
                "friendliness": state.friendliness,
                "annoyance": state.annoyance,
                "last_seen": int(datetime.now(UTC).isoformat()),
            }

            profile.data = data
            attributes.flag_modified(profile, "data")

            await session.commit()
