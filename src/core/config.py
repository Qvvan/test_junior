from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )


class PostgresConfig(ConfigBase):
    """Настройки базы данных"""
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", frozen=True)

    HOST: str
    PORT: int
    DATABASE: str
    USER: str
    PASSWORD: SecretStr

    ECHO: bool = False
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10


class AppConfig(ConfigBase):
    """Основные настройки приложения"""
    model_config = SettingsConfigDict(env_prefix="APP_", frozen=True)

    DEBUG: bool
    SECRET_KEY: str
    AUTH_ACCESS_TOKEN_TTL_MINUTES: int = 15
    AUTH_REFRESH_TOKEN_TTL_DAYS: int = 30
    AUTH_PASSWORD_RESET_TTL_MINUTES: int = 30


class Config(ConfigBase):
    """Главный класс конфигурации"""

    app: AppConfig = Field(default_factory=AppConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)

    @classmethod
    def load(cls, env_file: str | Path = ".env") -> "Config":
        env_path = Path(env_file).resolve()

        if not env_path.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {env_path}")

        load_dotenv(dotenv_path=env_path)
        return cls()
