from __future__ import annotations

import math
from typing import Protocol

from app.config import Settings


# Every embedding provider exposes the same interface so retrieval can switch providers without API churn.
class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


def normalize_vector(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector

    return [value / magnitude for value in vector]


# This dev embedder hashes tokens into a fixed-width vector so retrieval can be tested offline.
class DeterministicEmbeddingProvider:
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_single_text(text)

    # A single-text helper keeps the provider logic readable while still sharing normalization behavior.
    def _embed_single_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions

        for token in text.lower().split():
            slot = hash(token) % self.dimensions
            vector[slot] += 1.0

        return normalize_vector(vector)


class OpenAIEmbeddingProvider:
    def __init__(self, settings: Settings) -> None:
        from openai import OpenAI

        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        request_args: dict[str, object] = {
            "input": texts,
            "model": self.settings.openai_embedding_model,
        }
        if self.settings.openai_embedding_model.startswith("text-embedding-3"):
            request_args["dimensions"] = self.settings.embedding_dimensions

        response = self.client.embeddings.create(**request_args)
        return [normalize_vector(list(item.embedding)) for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    # OpenAI embeddings are used only when explicitly configured so local development stays frictionless.
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("RAG_OPENAI_API_KEY must be set when embedding_provider is 'openai'.")
        return OpenAIEmbeddingProvider(settings)

    return DeterministicEmbeddingProvider(settings.embedding_dimensions)


# Cosine similarity is the core retrieval metric for the first MVP.
def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
