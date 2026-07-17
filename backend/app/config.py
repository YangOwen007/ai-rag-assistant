from pydantic import BaseModel, Field


# This settings model keeps the first MVP configuration explicit and easy to inspect.
class Settings(BaseModel):
    app_name: str = "AI RAG Assistant"
    chunk_size: int = Field(default=600, ge=200, le=2000)
    chunk_overlap: int = Field(default=120, ge=20, le=400)
    embedding_dimensions: int = Field(default=128, ge=32, le=2048)
    top_k: int = Field(default=4, ge=1, le=10)


settings = Settings()

