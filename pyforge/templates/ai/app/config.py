"""
Typed settings for the AI application, loaded from .env.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "{{ project_name }}"
    app_env: str = "development"
    debug: bool = True

    # LLM — OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # LLM — Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Vector store
    chroma_persist_dir: str = "./chroma_db"
{% if postgres %}
    # pgvector
    pgvector_url: str = ""
{% endif %}
{% if redis %}
    # Redis
    redis_url: str = "redis://localhost:6379/0"
{% endif %}

    # LangSmith tracing (set via env vars)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "{{ project_name }}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
