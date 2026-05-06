import os
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from src.i18n import PersonalityToneType


class DatabaseConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    name: str = "postgres"
    driver: str = "postgresql+asyncpg"

    def build_url(self):
        return URL.create(
            drivername=self.driver,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


class FileLoggingConfig(BaseModel):
    enabled: bool = True
    directory: str = "logs"
    encoding: str = "utf-8"


class ConsoleLoggingConfig(BaseModel):
    rich_tracebacks: bool = True
    markup: bool = True


class LoggerConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    file_logging: FileLoggingConfig = Field(default_factory=FileLoggingConfig)
    console_logging: ConsoleLoggingConfig = Field(default_factory=ConsoleLoggingConfig)


class BotSettings(BaseSettings):
    discord_token: str = Field(default_factory=lambda: os.getenv("DISCORD_TOKEN", ""))
    database_config: DatabaseConfig = Field(default_factory=DatabaseConfig)

    bot_name: str = "TehBot"
    default_language: str = "en"
    bot_prefix: str = "pox/"
    default_personality: str = PersonalityToneType.CASUAL.value

    logger: LoggerConfig = Field(default_factory=LoggerConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
