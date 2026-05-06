from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GuildConfig(Base):
    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)


class UserXP(Base):
    __tablename__ = "user_xp"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    xp: Mapped[int] = mapped_column(BigInteger, default=0)
    level: Mapped[int] = mapped_column(BigInteger, default=0)


class CommandUsage(Base):
    __tablename__ = "command_usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)

    command: Mapped[str] = mapped_column(String(100), index=True)

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )


class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    locale: Mapped[str | None] = mapped_column(String(16), nullable=True)

    data: Mapped[dict] = mapped_column(JSONB, default=dict)
