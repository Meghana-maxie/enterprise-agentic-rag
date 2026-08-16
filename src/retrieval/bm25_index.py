"""In-memory BM25Okapi lexical search index with disk persistence."""

import re
import pickle
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from src.ingestion.chunker import TextChunk
from config.settings import settings


class BM25Index:
    """Sparse lexical search index utilizing BM25Okapi."""

    def __init__(self, storage_path: str = settings.BM25_INDEX_PATH):
        self.storage_path = Path(storage_path)
        self.chunks: List[TextChunk] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: BM25Okapi | None = None
        self._load_if_exists()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple, fast regex-based lowercase tokenizer."""
        return re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())

    def build_index(self, chunks: List[TextChunk]) -> None:
        """Construct BM25 index from a list of TextChunk objects and persist to disk."""
        self.chunks = list(chunks)
        self.tokenized_corpus = [self.tokenize(c.content) for c in self.chunks]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None
        self.save()

    def add_chunks(self, new_chunks: List[TextChunk]) -> None:
        """Append new chunks to existing index."""
        combined = self.chunks + new_chunks
        self.build_index(combined)

    def search(self, query: str, limit: int = settings.TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """Perform lexical keyword search scoring with BM25."""
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = self.tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        scored_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:limit]

        results: List[Dict[str, Any]] = []
        for idx, score in scored_indices:
            if score > 0:
                chunk = self.chunks[idx]
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "doc_name": chunk.doc_name,
                    "page_number": chunk.page_number,
                    "score": float(score),
                    "metadata": chunk.metadata,
                })

        return results

    def save(self) -> None:
        """Persist BM25 index and chunk payload to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "chunks": self.chunks,
            "tokenized_corpus": self.tokenized_corpus,
            "bm25": self.bm25
        }
        with open(self.storage_path, "wb") as f:
            pickle.dump(payload, f)

    def _load_if_exists(self) -> None:
        """Load persisted index from disk if present."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "rb") as f:
                    payload = pickle.load(f)
                    self.chunks = payload.get("chunks", [])
                    self.tokenized_corpus = payload.get("tokenized_corpus", [])
                    self.bm25 = payload.get("bm25", None)
            except Exception:
                self.chunks = []
                self.tokenized_corpus = []
                self.bm25 = None
