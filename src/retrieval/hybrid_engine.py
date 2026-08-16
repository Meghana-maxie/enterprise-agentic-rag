"""Hybrid Search Engine combining Dense Vector Search, Sparse BM25, RRF, and Cross-Encoder Reranking."""

from typing import List, Dict, Any
from collections import defaultdict
from src.retrieval.qdrant_store import QdrantVectorStore
from src.retrieval.bm25_index import BM25Index
from src.retrieval.reranker import LocalReranker
from src.ingestion.chunker import TextChunk
from config.settings import settings


class HybridSearchEngine:
    """Enterprise Hybrid Search Orchestrator with Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        vector_store: QdrantVectorStore | None = None,
        bm25_index: BM25Index | None = None,
        reranker: LocalReranker | None = None,
        rrf_k: int = settings.RRF_K
    ):
        self.vector_store = vector_store or QdrantVectorStore()
        self.bm25_index = bm25_index or BM25Index()
        self.reranker = reranker or LocalReranker()
        self.rrf_k = rrf_k

    def index_chunks(self, chunks: List[TextChunk]) -> Dict[str, int]:
        """Index chunks across both Dense Qdrant and Sparse BM25 stores."""
        dense_count = self.vector_store.add_chunks(chunks)
        self.bm25_index.add_chunks(chunks)
        return {"dense_indexed": dense_count, "bm25_indexed": len(chunks)}

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply Reciprocal Rank Fusion (RRF) to blend ranked dense and sparse search lists."""
        rrf_scores: Dict[str, float] = defaultdict(float)
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Process dense rankings
        for rank, doc in enumerate(dense_results, start=1):
            chunk_id = doc["chunk_id"]
            rrf_scores[chunk_id] += 1.0 / (self.rrf_k + rank)
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = doc

        # Process sparse rankings
        for rank, doc in enumerate(sparse_results, start=1):
            chunk_id = doc["chunk_id"]
            rrf_scores[chunk_id] += 1.0 / (self.rrf_k + rank)
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = doc

        # Sort all unique documents by cumulative RRF score
        sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        fused_results: List[Dict[str, Any]] = []
        for cid in sorted_chunk_ids:
            item = dict(chunk_map[cid])
            item["rrf_score"] = float(rrf_scores[cid])
            fused_results.append(item)

        return fused_results

    def search(
        self,
        query: str,
        retrieval_limit: int = settings.TOP_K_RETRIEVAL,
        rerank_limit: int = settings.TOP_K_RERANK
    ) -> List[Dict[str, Any]]:
        """Execute complete Hybrid Search pipeline: Dense + Sparse -> RRF Fusion -> Local Rerank."""
        # 1. Parallel retrieval from dense and sparse stores
        dense_hits = self.vector_store.search(query, limit=retrieval_limit)
        sparse_hits = self.bm25_index.search(query, limit=retrieval_limit)

        # 2. Reciprocal Rank Fusion
        fused_hits = self.reciprocal_rank_fusion(dense_hits, sparse_hits)

        # 3. Local Cross-Encoder Reranking on fused top candidates
        reranked_hits = self.reranker.rerank(
            query=query,
            documents=fused_hits[:retrieval_limit],
            top_n=rerank_limit
        )

        return reranked_hits
