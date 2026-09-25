from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx


def tokens(text: str) -> list[str]:
    raw = re.findall(r"[a-z0-9]+", text.lower())
    aliases = {
        "cancellation": "cancel",
        "cancellations": "cancel",
        "cancelled": "cancel",
        "cancelling": "cancel",
        "returns": "return",
        "returned": "return",
        "damaged": "damage",
        "deliveries": "delivery",
    }
    return [aliases.get(token, token) for token in raw]


@dataclass(frozen=True)
class Chunk:
    document_id: str
    chunk_id: str
    title: str
    text: str


class SearchIndex(Protocol):
    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]: ...


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


def load_policy_chunks(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        body = parts[2] if len(parts) == 3 else content
        document_id = path.stem
        title = document_id.replace("-", " ").title()
        current_title = title
        current: list[str] = []
        index = 0
        for line in body.splitlines():
            if line.startswith("#"):
                if current:
                    index += 1
                    chunks.append(Chunk(document_id, f"{document_id}-{index:02d}", current_title, "\n".join(current).strip()))
                    current = []
                current_title = line.lstrip("# ").strip()
            elif line.strip():
                current.append(line.strip())
        if current:
            index += 1
            chunks.append(Chunk(document_id, f"{document_id}-{index:02d}", current_title, "\n".join(current).strip()))
    if not chunks:
        raise ValueError(f"No policy chunks found in {directory}")
    return chunks


class BM25Index:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks, self.k1, self.b = chunks, k1, b
        self.documents = [tokens(f"{chunk.title} {chunk.text}") for chunk in chunks]
        self.average_length = sum(map(len, self.documents)) / len(self.documents)
        self.document_frequency: dict[str, int] = {}
        for document in self.documents:
            for token in set(document):
                self.document_frequency[token] = self.document_frequency.get(token, 0) + 1

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        query_tokens = tokens(query)
        scored: list[tuple[Chunk, float]] = []
        total = len(self.documents)
        for chunk, document in zip(self.chunks, self.documents, strict=True):
            score = 0.0
            frequencies = {token: document.count(token) for token in set(query_tokens)}
            for token in query_tokens:
                frequency = frequencies.get(token, 0)
                if not frequency:
                    continue
                df = self.document_frequency.get(token, 0)
                idf = math.log(1 + (total - df + 0.5) / (df + 0.5))
                denominator = frequency + self.k1 * (1 - self.b + self.b * len(document) / self.average_length)
                score += idf * frequency * (self.k1 + 1) / denominator
            scored.append((chunk, score))
        return sorted(scored, key=lambda item: (-item[1], item[0].chunk_id))[:top_k]


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Embedding vectors must have the same non-zero dimension")
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class OllamaEmbedder:
    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 60,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = httpx.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": texts},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        vectors = response.json().get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise ValueError("Embedding response did not match the requested inputs")
        return [[float(value) for value in vector] for vector in vectors]


class DenseIndex:
    def __init__(self, chunks: list[Chunk], embedder: Embedder):
        self.chunks = chunks
        self.embedder = embedder
        inputs = [f"{chunk.title}\n{chunk.text}" for chunk in chunks]
        self.vectors = embedder.embed(inputs)
        if len(self.vectors) != len(chunks):
            raise ValueError("Embedding count must match chunk count")

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        query_vectors = self.embedder.embed([query])
        if len(query_vectors) != 1:
            raise ValueError("Expected one query embedding")
        scored = [
            (chunk, _cosine(query_vectors[0], vector))
            for chunk, vector in zip(self.chunks, self.vectors, strict=True)
        ]
        return sorted(scored, key=lambda item: (-item[1], item[0].chunk_id))[:top_k]


class HybridRRFIndex:
    """Fuse lexical and dense ranks with reciprocal rank fusion."""

    def __init__(
        self,
        lexical: SearchIndex,
        dense: SearchIndex,
        rank_constant: int = 60,
        candidate_k: int = 20,
    ):
        if rank_constant <= 0 or candidate_k <= 0:
            raise ValueError("RRF parameters must be positive")
        self.lexical = lexical
        self.dense = dense
        self.rank_constant = rank_constant
        self.candidate_k = candidate_k

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        scores: dict[str, float] = {}
        chunks: dict[str, Chunk] = {}
        for ranking in (
            self.lexical.search(query, self.candidate_k),
            self.dense.search(query, self.candidate_k),
        ):
            for rank, (chunk, _) in enumerate(ranking, start=1):
                chunks[chunk.chunk_id] = chunk
                scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (
                    self.rank_constant + rank
                )
        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:top_k]
        return [(chunks[chunk_id], score) for chunk_id, score in ordered]
