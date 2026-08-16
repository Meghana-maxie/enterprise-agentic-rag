"""Unit tests for Document Chunking, BM25 Index, and Hybrid Search Engine."""

import pytest
from src.ingestion.loaders import LoadedPage
from src.ingestion.chunker import RecursiveChunker
from src.retrieval.bm25_index import BM25Index
from src.retrieval.hybrid_engine import HybridSearchEngine


def test_recursive_chunker_metadata_preservation():
    """Verify recursive chunker splits text properly and preserves document metadata."""
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
    pages = [
        LoadedPage(
            doc_name="test_doc.md",
            page_number=1,
            text="First sentence about cloud computing.\n\nSecond paragraph discussing high availability and SLA of 99.99%.\n\nThird paragraph on CockroachDB.",
            metadata={"author": "DevOps"}
        )
    ]
    chunks = chunker.chunk_pages(pages)

    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.doc_name == "test_doc.md"
        assert chunk.page_number == 1
        assert len(chunk.content) > 0
        assert chunk.chunk_id is not None
        assert chunk.metadata["author"] == "DevOps"


def test_bm25_lexical_indexing_and_search(tmp_path):
    """Verify BM25Okapi sparse retrieval precision."""
    storage_file = tmp_path / "test_bm25.pkl"
    index = BM25Index(storage_path=str(storage_file))

    chunker = RecursiveChunker(chunk_size=200, chunk_overlap=20)
    pages = [
        LoadedPage(doc_name="doc_a.txt", page_number=1, text="Kubernetes Karpenter autoscaling nodes on AMD EPYC processors."),
        LoadedPage(doc_name="doc_b.txt", page_number=1, text="AWS KMS encryption with customer-managed keys rotated every 90 days."),
    ]
    chunks = chunker.chunk_pages(pages)
    index.build_index(chunks)

    # Search for specific lexical terms
    results = index.search("KMS customer-managed keys", limit=2)
    assert len(results) >= 1
    assert results[0]["doc_name"] == "doc_b.txt"
    assert results[0]["score"] > 0


def test_reciprocal_rank_fusion():
    """Verify Reciprocal Rank Fusion (RRF) calculation mathematically."""
    engine = HybridSearchEngine(rrf_k=60)

    dense_results = [
        {"chunk_id": "chunk_1", "doc_name": "doc1.md", "content": "alpha"},
        {"chunk_id": "chunk_2", "doc_name": "doc2.md", "content": "beta"},
    ]
    sparse_results = [
        {"chunk_id": "chunk_2", "doc_name": "doc2.md", "content": "beta"},
        {"chunk_id": "chunk_3", "doc_name": "doc3.md", "content": "gamma"},
    ]

    fused = engine.reciprocal_rank_fusion(dense_results, sparse_results)

    # chunk_2 appears in both dense (rank 2) and sparse (rank 1), so it should score highest
    assert len(fused) == 3
    assert fused[0]["chunk_id"] == "chunk_2"
    assert fused[0]["rrf_score"] > fused[1]["rrf_score"]
