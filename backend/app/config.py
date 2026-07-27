from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# This settings model reads from environment variables so local and deployed setups can diverge cleanly.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "AI RAG Assistant"
    database_url: str = "sqlite:///./rag_assistant.db"
    embedding_provider: Literal["deterministic", "openai"] = "deterministic"
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    chunk_size: int = Field(default=600, ge=200, le=2000)
    chunk_overlap: int = Field(default=120, ge=20, le=400)
    embedding_dimensions: int = Field(default=128, ge=32, le=2048)
    top_k: int = Field(default=4, ge=1, le=10)

    # These helpers make the storage and retrieval branches easier to reason about elsewhere in the app.
    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


settings = Settings()
