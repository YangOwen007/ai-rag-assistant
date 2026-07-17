from __future__ import annotations

from app.models import Chunk
from app.services.embeddings import DeterministicEmbedder, cosine_similarity


# This simple index keeps the retrieval story understandable before we add database persistence.
class InMemoryChunkIndex:
    def __init__(self, embedder: DeterministicEmbedder) -> None:
        self.embedder = embedder
        self._chunks: list[Chunk] = []

    def add_chunks(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            chunk.embedding = self.embedder.embed(chunk.text)
            self._chunks.append(chunk)

    def search(self, question: str, top_k: int) -> list[tuple[Chunk, float]]:
        query_embedding = self.embedder.embed(question)
        ranked = [
            (chunk, cosine_similarity(query_embedding, chunk.embedding))
            for chunk in self._chunks
        ]
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[:top_k]

    def count(self) -> int:
        return len(self._chunks)

