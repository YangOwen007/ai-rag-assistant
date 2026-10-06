from typing import Literal

from pydantic import Field, model_validator
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
    embedding_dimensions: Literal[128] = 128
    top_k: int = Field(default=4, ge=1, le=10)
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    max_upload_bytes: int = Field(default=5 * 1024 * 1024, ge=1024, le=20 * 1024 * 1024)
    max_text_chars: int = Field(default=100_000, ge=50, le=100_000)

    @model_validator(mode="after")
    def validate_chunk_settings(self):
        # Overlap must be smaller than the window to avoid excessive duplicate chunks.
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self

    # These helpers make the storage and retrieval branches easier to reason about elsewhere in the app.
    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


settings = Settings()
