from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path


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
