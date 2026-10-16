
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise Agentic RAG"
    app_env: str = "development"
    gemini_model: str = "gemini-2.5-flash"

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768
    langgraph_checkpoint_url: str

    gemini_api_key: str | None = None
    jev_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
