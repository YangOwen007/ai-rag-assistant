from __future__ import annotations

import math


# This dev embedder hashes tokens into a fixed-width vector so retrieval can be tested offline.
class DeterministicEmbedder:
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions

        for token in text.lower().split():
            slot = hash(token) % self.dimensions
            vector[slot] += 1.0

        return self._normalize(vector)

    def _normalize(self, vector: list[float]) -> list[float]:
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]


# Cosine similarity is the core retrieval metric for the first MVP.
def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))

