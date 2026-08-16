"""Unit tests for Document Chunking, BM25 Index, Qdrant Vector Store, and Hybrid Search Engine."""

import pytest
from src.ingestion.loaders import LoadedPage
from src.ingestion.chunker import RecursiveChunker
from src.retrieval.bm25_index import BM25Index
from src.retrieval.qdrant_store import QdrantVectorStore
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
    # dense score: 1/(60+2) = 1/62 = 0.016129
    # sparse score: 1/(60+1) = 1/61 = 0.016393
    # total chunk_2 score: 0.032522 vs chunk_1: 1/(60+1)=0.016393
    assert len(fused) == 3
    assert fused[0]["chunk_id"] == "chunk_2"
    assert fused[0]["rrf_score"] > fused[1]["rrf_score"]
    assert pytest.approx(fused[0]["rrf_score"], 0.0001) == (1/62 + 1/61)


def test_qdrant_vector_store_real_insertion_and_search(tmp_path):
    """Verify real Qdrant vector store inserts embeddings and performs cosine similarity search."""
    storage_dir = tmp_path / "test_qdrant"
    store = QdrantVectorStore(
        collection_name="test_collection",
        storage_path=str(storage_dir)
    )

    chunker = RecursiveChunker(chunk_size=200, chunk_overlap=20)
    pages = [
        LoadedPage(doc_name="cloud.md", page_number=1, text="The platform operates across us-east-1, eu-west-1, and ap-southeast-1."),
        LoadedPage(doc_name="security.md", page_number=1, text="All customer data is encrypted using AES-256 with KMS keys."),
    ]
    chunks = chunker.chunk_pages(pages)
    count = store.add_chunks(chunks)
    assert count == 2

    # Query semantic vector search
    hits = store.search("geographic regions and availability zones", limit=2)
    assert len(hits) == 2
    assert hits[0]["doc_name"] == "cloud.md"
    assert hits[0]["score"] > 0.3
