from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LoggingConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="LOG_", frozen=True)

    LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    JSON_FORMAT: bool = True


class PostgresConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", frozen=True)

    HOST: str
    PORT: int
    DATABASE: str
    USER: str
    PASSWORD: SecretStr

    POOL_SIZE: int = 5


class AppConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="APP_", frozen=True)

    DEBUG: bool
    SECRET_KEY: SecretStr
    AUTH_ACCESS_TOKEN_TTL_MINUTES: int = 15
    AUTH_REFRESH_TOKEN_TTL_DAYS: int = 30
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])


class Config(ConfigBase):
    app: AppConfig = Field(default_factory=AppConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
