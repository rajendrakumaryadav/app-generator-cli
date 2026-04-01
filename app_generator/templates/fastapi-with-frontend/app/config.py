"""
Typed application settings loaded from environment variables / .env file.
"""
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "{{ project_name }}"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./{{ package_name }}.db"
{% if redis %}
    # Redis
    redis_url: str = "redis://localhost:6379/0"
{% endif %}

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
