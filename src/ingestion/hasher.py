"""Deterministic hashing utility for document chunks and deduplication."""

import hashlib


def generate_chunk_id(doc_name: str, page_number: int, content: str) -> str:
    """Generate a deterministic, collision-resistant SHA-256 hash ID for a document chunk."""
    raw_key = f"{doc_name}:{page_number}:{content.strip()}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]


def compute_content_hash(text: str) -> str:
    """Generate a SHA-256 hash for raw document content to detect file updates."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
